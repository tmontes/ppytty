km = {
    b'[': 'prev',
    b']': 'next',
    b'r': 'redo',
}

ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Serial([
        ppytty.Label('first label'),
        ppytty.Loop(ppytty.DelayReturn(seconds=3)),
    ]),
    ppytty.Serial([
        ppytty.Label('second label'),
        ppytty.Loop(ppytty.DelayReturn(seconds=3)),
    ]),
    ppytty.Serial([
        ppytty.Label('third label'),
        ppytty.Loop(ppytty.DelayReturn(seconds=3)),
    ]),
], name='outer')
