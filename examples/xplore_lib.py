
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets, geometry


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
            Text(
                ("EXPLORING ppytty's LIB", '{slide_title}'),
                id='top-template-bar',
                use_context=True,
                geometry=geometry.horizontal_bar(height=4),
                padding=(1, 2),
            ),
            Text(
                '{slide_number}/{slide_count}',
                id='bottom-template-bar',
                text_align=Text.Align.RIGHT,
                use_context=True,
                geometry=geometry.horizontal_bar(height=1, from_top=False),
                padding=(0, 2),
            ),
        ])
        super().__init__(title=title, widgets=widgets, template=template)



long_welcome_text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae magna eget quam euismod bibendum eget mattis enim. Sed eu elementum nunc. Vestibulum aliquam consectetur semper. Phasellus viverra luctus nisl ut pulvinar. Duis lobortis vulputate mauris. In nec luctus eros. Ut tristique purus eu nunc porttitor, quis placerat nulla malesuada. Vivamus ante turpis, convallis et ex in, posuere maximus turpis. In mattis in dui ac fermentum.
"""

ppytty_task = SlideDeck([
    MySlide(title='Welcome', widgets=[
        Text((
                'welcome text',
                'text widgets handle multiple paragraphs',
                long_welcome_text,
            ),
            text_align=Text.Align.CENTER,
            paragraph_spacing=1,
            padding=(1, 2),
        ),
        Bullets(['welcome bullet 1', 'welcome bullet 2'], at_once=True),
    ]),
    MySlide(title='[content]', widgets=[
        Text('content text #1'),
        Bullets(['bullet 1', 'bullet 2']),
        Text('content text #3'),
    ]),
    MySlide(title='Thanks!', widgets=[
        # Overriding template suggested geometry: go big!
        Text('by bye text', geometry=dict(x=0.1, y=0.2, w=0.8, h=0.8, dh=-2)),
    ]),
])


