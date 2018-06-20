
import random

import ppytty


class WindowExerciser(ppytty.Task):

    def run(self):

        w1 = yield ('window-create', 5, 3, 40, 15, 31)
        w2 = yield ('window-create', 35, 12, 40, 15, 39)

        w1.print('Bottom window'.center(40), bg=17)
        w2.print('Top window'.center(40), bg=19)

        w1.print('\x1b[2;15r')  # ideally implemented as window.set_scroll_lines
        w2.print('\x1b[2;15r')
        w1.print('\x1b[2;1H')   # ideally implemented as window.move_cursor
        w2.print('\x1b[2;1H')

        yield ('window-render', w2)
        yield ('sleep', 0.25)
        yield ('window-render', w1)

        yield ('sleep', 1)

        words = 'the quick brown fox jumps over the lazy dog'.split()
        windows = (w1, w2)

        while True:
            window = random.choice(windows)
            word = random.choice(words)
            window.print(word + ' ')
            yield ('window-render', window)
            yield ('sleep', 0.02)


ppytty_task = WindowExerciser()