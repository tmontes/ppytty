# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import argparse
import logging
import os
import runpy
import sys

import ppytty

from . import default



log = logging.getLogger(__name__)


def setup_logging(log_filename, log_level_specs):

    if not log_filename:
        return
    handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname).1s %(name)s %(message)s',
        datefmt='%H:%M:%S',)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if not log_level_specs:
        root_logger.setLevel(logging.WARNING)
        return
    for log_level_spec in log_level_specs:
        left, _, right = log_level_spec.partition(':')
        logger_name, level = (left, right) if right else ('', left)
        try:
            level = getattr(logging, level.upper())
        except AttributeError as e:
            msg = f'invalid log level {level!r}'
            if logger_name:
                msg += f' for {logger_name!r}'
            msg += ': use one of [debug|info|warn|error]'
            raise RuntimeError(msg) from e
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)



def parse_arguments(argv=sys.argv, env=os.environ):

    arg_list = env.get('PPYTTY', '').split()
    arg_list.extend(argv[1:])

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--version', action='store_true')
    arg_parser.add_argument('-l', metavar='<log-filename>',
                            dest='log_filename', help='no logging if omitted')
    arg_parser.add_argument('-L', metavar='<log-level-spec>', action='append',
                            dest='log_level_specs', help="""<log-level-spec> is
                            [<logger-name>:]<level>, <level> is
                            [debug|info|warn|error|critical]""")
    arg_parser.add_argument('script', nargs='?')

    return arg_parser.parse_args(arg_list)



def task_from_args(args, task=default.TASK):

    if not args.script:
        return task

    try:
        script_globals = runpy.run_path(args.script)
    except Exception as e:
        raise RuntimeError(f'failed running {args.script!r}: {e}') from e

    TASK_NAME_IN_SCRIPT = 'ppytty_task'
    try:
        task = script_globals[TASK_NAME_IN_SCRIPT]
    except KeyError as e:
        raise RuntimeError(f'no {TASK_NAME_IN_SCRIPT!r} global in {args.script!r}') from e

    return task



def main():

    args = parse_arguments()

    if args.version:
        print(ppytty.__version__)
        return 0

    try:
        setup_logging(args.log_filename, args.log_level_specs)
    except RuntimeError as e:
        print(e)
        return -1
    except OSError as e:
        print('failed opening output log file:', e)
        return -1

    try:
        task = task_from_args(args)
    except RuntimeError as e:
        log.error('%s', e, exc_info=True)
        print(e)
        return -2

    ppytty.run(task, post_prompt='[COMPLETED]')

    return 0


if __name__ == '__main__':

    sys.exit(main())

# ----------------------------------------------------------------------------
