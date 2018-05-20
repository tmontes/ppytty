ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Slide([
        ppytty.InnerSequenceKeyboard([
            ppytty.Label('1.1/3. Hello world!', name='l1'),
            ppytty.Label('1.2/3. And more...', name='l2'),
            ppytty.Label('1.3/3.Done with the first slide!', name='l3'),
        ], name='s1.d1'),
    ], name='s1'),
    ppytty.Slide([
        ppytty.Label('2.1/1....nearly done', name='l3'),
    ], name='s2'),
    ppytty.Slide([
        ppytty.Label('3.1/2. Last slide here', name='l4'),
        ppytty.Label('3.2/2. ...bye!', name='l5'),
    ], name='s3'),
], name='deck')
