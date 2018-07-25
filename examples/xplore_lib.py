
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets

t = SlideTemplate(widgets=[
    Text('template text'),
])

ppytty_task = SlideDeck([
    Slide(title='Welcome', template=t, widgets=[
        Text('welcome text'),
        Bullets(['welcome bullet 1', 'welcome bullet 2'], at_once=True),
    ]),
    Slide(title='[content]', template=t, widgets=[
        Text('content text #1'),
        Bullets(['bullet 1', 'bullet 2']),
        Text('content text #3'),
    ]),
    Slide(title='Thanks!', template=t, widgets=[
        Text('by bye text'),
    ]),
])


