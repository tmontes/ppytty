ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Slide([
        ppytty.InnerSequenceTimed([
            ppytty.Label('Hello world!', name='l1'),
            ppytty.Label('And more...', name='l2'),
            ppytty.Label('Done with the first slide!', name='l3'),
        ], name='s1seq', delay=1.2),
    ], name='s1'),
    ppytty.Slide([
        ppytty.Label('...nearly done', name='l3'),
    ], name='s2'),
    ppytty.Slide([
        ppytty.Label('Last slide here', name='l4'),
        ppytty.Label('...bye!', name='l5'),
    ], name='s3'),
], name='deck')
