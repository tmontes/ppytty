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



def _setup_logging(log_filename=None, log_level_specs=None):

    root_logger = logging.getLogger()
    handler = logging.FileHandler(log_filename) if log_filename else logging.NullHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname).1s %(name)s %(message)s',
        datefmt='%H:%M:%S',)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    if not log_filename or not log_level_specs:
        root_logger.setLevel(logging.WARNING)
        return
    for log_level_spec in log_level_specs:
        left, _, right = log_level_spec.partition(':')
        logger_name, level = (left, right) if right else ('', left)
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            msg = f'invalid log level {level!r}'
            if logger_name:
                msg += f' for {logger_name!r}'
            msg += ': use one of [debug|info|warn|error]'
            raise RuntimeError(msg)
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)



def main(argv=sys.argv, env=os.environ, task=default.TASK):

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
    args = arg_parser.parse_args(arg_list)

    if args.version:
        print(ppytty.__version__)
        return 0

    try:
        _setup_logging(args.log_filename, args.log_level_specs)
    except RuntimeError as e:
        print(e)
        return -1

    if args.script:
        try:
            script = runpy.run_path(args.script, init_globals={'ppytty': ppytty})
        except Exception as e:
            print(f'failed running {args.script!r}: {e}')
            return -2
        TASK_NAME_IN_SCRIPT = 'ppytty_task'
        try:
            task = script[TASK_NAME_IN_SCRIPT]
        except KeyError as e:
            print(f'no {TASK_NAME_IN_SCRIPT!r} global in {args.script!r}')
            return -3

    ppytty.run(task)

    return 0


if __name__ == '__main__':

    sys.exit(main())

# ----------------------------------------------------------------------------
