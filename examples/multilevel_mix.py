ppytty_task = ppytty.OuterSequenceKeyboard([
    ppytty.Slide([
        ppytty.InnerSequenceTimed([
            ppytty.Label('1.1/3. Hello world!', name='s1.l1'),
            ppytty.Label('1.2/3. And more...', name='s1.l2'),
            ppytty.Label('1.3/3. Done with the first slide!', name='s1.l3'),
        ], name='s1.d1', min_delay=0.25, max_delay=1),
    ], name='s1'),
    ppytty.Slide([
        ppytty.InnerSequenceTimed([
            ppytty.Label('2.1/2. Slide 2 line 1!', name='s2.l1'),
            ppytty.Label('2.2/2. Last line for slide 2', name='s2.l2'),
        ], name='s2.d1', min_delay=0.25, max_delay=1),
    ], name='s2'),
    ppytty.Slide([
        ppytty.InnerSequenceTimed([
            ppytty.Label('3.1/5. ...last slide', name='s3.l1'),
            ppytty.Label('3.2/5. ...with...', name='s3.l2'),
            ppytty.Label('3.3/5. ...five...', name='s3.l3'),
            ppytty.Label('3.4/5. ...different...', name='s3.l4'),
            ppytty.Label('3.5/5. ...lines!', name='s3.l5'),
        ], name='s3.d1', min_delay=0.25, max_delay=1),
    ], name='s3'),
], name='deck')
