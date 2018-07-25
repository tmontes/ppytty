
from ppytty import SlideDeck, Slide, SlideTemplate, Text

t = SlideTemplate(widgets=[
    Text('template widget'),
])

ppytty_task = SlideDeck([
    Slide(title='Welcome', template=t, widgets=[1]),
    Slide(title='[content]', template=t, widgets=[1, 2, 3]),
    Slide(title='Thanks!', template=t, widgets=[1]),
])


