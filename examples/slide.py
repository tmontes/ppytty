import ppytty

ppytty_task = ppytty.Slide([
    ppytty.Label('Hello world!'),
    ppytty.Serial([
        ppytty.Label('Bye...'),
        ppytty.Label('Bye Bye...'),
    ]),
])
