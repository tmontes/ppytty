
import random

import ppytty


class WindowExerciser(ppytty.Task):

    def run(self):

        w1 = yield ('window-create', 5, 3, 40, 15, 31)
        w2 = yield ('window-create', 35, 12, 40, 15, 39)

        w1.print('Bottom window'.center(40), bg=17)
        w2.print('Top window'.center(40), bg=19)

        w1.print('\x1b[2;15r')  # TODO: implement as window.set_scroll_lines?
        w2.print('\x1b[2;15r')
        w1.print('\x1b[2;1H')   # TODO: implement as window.move_cursor?
        w2.print('\x1b[2;1H')

        yield ('window-render', w2)
        yield ('sleep', 0.2)
        yield ('window-render', w1)

        yield ('sleep', 0.2)

        words = 'the quick brown fox jumps over the lazy dog'.split()
        windows = (w1, w2)

        for _ in range(42):
            window = random.choice(windows)
            word = random.choice(words)
            window.print(word + ' ')
            yield ('window-render', window)
            yield ('sleep', 0.05)

        yield ('window-destroy', w1)

        yield ('state-dump', 'MY TAG')

        yield ('sleep', 2)


class Parent(ppytty.Task):

    def run(self):

        child = WindowExerciser()
        yield ('task-spawn', child)
        # yield ('sleep', 1)
        # yield ('task-destroy', child)
        result = yield ('task-wait', )
        # yield ('direct-print', f'child result={result!r}')


ppytty_task = Parent()