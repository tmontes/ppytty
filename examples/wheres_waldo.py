
import itertools
import random

import ppytty


class Pulse(ppytty.Task):

    def __init__(self, x, y, msgs, predelay=0, delay=0.015, **kw):
        super().__init__(**kw)
        self._x = int(x)
        self._y = int(y)
        self.set_msgs(msgs)
        self._predelay = predelay
        self._delay = delay

    def __repr__(self):
        return f'<Pulse {self._x}.{self._y}>'

    def set_msgs(self, msgs):
        self._msgs = itertools.cycle(msgs)

    def run(self):
        min_color = 232
        max_color = 255
        fade_in = range(min_color, max_color+1)
        fade_out = range(max_color-1, min_color, -1)
        yield ('sleep', self._predelay)
        normal = '\x1b[39m'
        for msg in self._msgs:
            for fg in itertools.chain(fade_in, fade_out):
                output = f'\x1b[38;5;{fg}m{msg}{normal}'
                yield ('print-at', self._x, self._y, output)
                yield ('sleep', self._delay)



phrases = [
    "Load testing ppytty's runner",
    'How about this?!',
    'Hello World!',
    '...flashy but not really useful.',
    'Fading in and out...',
    'The quick brown fox jumps over the lazy dog.',
    'Do we really need window based output?',
]

pulses = [
    Pulse(
        x=((i * 12) + random.randint(0, 3)) % 80,
        y=int((i * 12) / 80)*2,
        msgs=(s.center(10) for s in random.choice(phrases).split()),
        predelay=random.randint(0, 1000) / 100,
        delay=random.randint(10, 30) / 1000,
    ) for i in range(100)
]

random.choice(pulses).set_msgs(s.center(10) for s in 'Where is waldo?!'.split())

ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Slide([
        ppytty.Label(''),
        ppytty.Label('  Get ready to find Waldo...'),
    ]),
    ppytty.Slide(pulses),
    ppytty.Slide([
        ppytty.Label(''),
        ppytty.Label('  Did you find him?'),
    ]),
])
