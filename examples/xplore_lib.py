
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets


class MySlideTemplate(SlideTemplate):

    _GEOMETRIES = {
        1: {
            0: dict(x=0.4, y=0.4, w=0.2, h=0.2),
        },
        2: {
            0: dict(x=0.2, y=0.3, w=0.6, h=0.3, dy=-1),
            1: dict(x=0.2, y=0.6, w=0.6, h=0.3, dy=-1),
        },
        3: {
            0: dict(x=0.3, y=0.25, w=0.4, h=0.2, dy=+1),
            1: dict(x=0.3, y=0.45, w=0.4, h=0.2, dy=+1),
            2: dict(x=0.3, y=0.65, w=0.4, h=0.2, dy=+1),
        }
    }

    def geometry(self, widget_index, widget_count):

        return self._GEOMETRIES.get(widget_count, {}).get(widget_index)



class MySlide(Slide):

    def __init__(self, title, widgets):

        template = MySlideTemplate(widgets=[
            Text('template text', geometry=dict(x=0, y=1, w=1.0, h=4)),
        ])
        super().__init__(title=title, widgets=widgets, template=template)



ppytty_task = SlideDeck([
    MySlide(title='Welcome', widgets=[
        Text('welcome text'),
        Bullets(['welcome bullet 1', 'welcome bullet 2'], at_once=True),
    ]),
    MySlide(title='[content]', widgets=[
        Text('content text #1'),
        Bullets(['bullet 1', 'bullet 2']),
        Text('content text #3'),
    ]),
    MySlide(title='Thanks!', widgets=[
        # Overriding template suggested geometry: go big!
        Text('by bye text'), geometry=dict(x=0.1, y=0.2, w=0.8, h=0.8, dh=-1)),
    ]),
])


