
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets

t = SlideTemplate(widgets=[
    Text('template text', geometry=dict(x=0, y=1, w=1.0, h=4)),
])

ppytty_task = SlideDeck([
    Slide(title='Welcome', template=t, widgets=[
        Text(
            'welcome text',
            geometry=dict(x=0.3, y=0.4, w=0.4, h=0.2),
        ),
        Bullets(
            ['welcome bullet 1', 'welcome bullet 2'],
            at_once=True,
            geometry=dict(x=0.3, y=0.6, w=0.4, h=0.2),
        ),
    ]),
    Slide(title='[content]', template=t, widgets=[
        Text(
            'content text #1',
            geometry=dict(x=0.3, y=0.3, w=0.4, h=0.2),
        ),
        Bullets(
            ['bullet 1', 'bullet 2'],
            geometry=dict(x=0.3, y=0.5, w=0.4, h=0.2),
        ),
        Text(
            'content text #3',
            geometry=dict(x=0.3, y=0.7, w=0.4, h=0.2),
        ),
    ]),
    Slide(title='Thanks!', template=t, widgets=[
        Text(
            'by bye text',
            geometry=dict(x=0.3, y=0.3, w=0.4, h=0.4),
        ),
    ]),
])


