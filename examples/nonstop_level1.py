import ppytty

ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Serial([
        ppytty.Label('first label', name='l1'),
        ppytty.Loop(ppytty.DelayReturn(seconds=30, name='d1'), name='l1'),
    ], name='s1'),
    ppytty.Serial([
        ppytty.Label('second label', name='l2'),
        ppytty.Loop(ppytty.DelayReturn(seconds=30, name='d2'), name='l2'),
    ], name='s2'),
    ppytty.Serial([
        ppytty.Label('third label', name='l3'),
        ppytty.Loop(ppytty.DelayReturn(seconds=30, name='d3'), name='l3'),
    ], name='s3'),
], name='outer')
