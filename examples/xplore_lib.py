
from ppytty import SlideDeck, Slide, SlideTemplate, Text

t = SlideTemplate(widgets=[
    Text('template text'),
])

ppytty_task = SlideDeck([
    Slide(title='Welcome', template=t, widgets=[
        Text('welcome text'),
    ]),
    Slide(title='[content]', template=t, widgets=[
        Text('content text #1'),
        Text('content text #2'),
        Text('content text #3'),
    ]),
    Slide(title='Thanks!', template=t, widgets=[
        Text('by bye text'),
    ]),
])


