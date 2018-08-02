
import textwrap

from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets, geometry
from ppytty.kernel import api


class MySlideTemplate(SlideTemplate):

    pass

    # _GEOMETRIES = {
    #     1: {
    #         0: dict(x=0.4, y=0.4, w=0.2, h=0.2),
    #     },
    #     2: {
    #         0: dict(x=0.2, y=0.3, w=0.6, h=0.3, dy=-1),
    #         1: dict(x=0.2, y=0.6, w=0.6, h=0.3, dy=-1),
    #     },
    #     3: {
    #         0: dict(x=0.3, y=0.25, w=0.4, h=0.2, dy=+1),
    #         1: dict(x=0.3, y=0.45, w=0.4, h=0.2, dy=+1),
    #         2: dict(x=0.3, y=0.65, w=0.4, h=0.2, dy=+1),
    #     }
    # }

    # def geometry(self, widget_index, widget_count):

    #     return self._GEOMETRIES.get(widget_count, {}).get(widget_index)



# Slide.template = MySlideTemplate(widgets=[

SlideTemplate.widgets = [
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
]

SlideTemplate.widget_slots = {
    'top': geometry.horizontal_bar(height=8, margin=6, dx=10, dw=-20),
    'mid': geometry.horizontal_bar(height=6, margin=15, dx=10, dw=-20),
    'bottom': geometry.horizontal_bar(height=5, margin=22, dx=10, dw=-20),
}


Text.padding = (1, 2)


# ------------------------------------------------------------------------------
# Slide #1

text_widget = Text([
        'welcome text',
        'text widgets handle multiple paragraphs',
        textwrap.dedent("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae
        magna eget quam euismod bibendum eget mattis enim. Sed eu elementum
        nunc. Vestibulum aliquam consectetur semper. Phasellus viverra luctus
        nisl ut pulvinar. Duis lobortis vulputate mauris. In nec luctus eros.
        Ut tristique purus eu nunc porttitor, quis placerat nulla malesuada.
        Vivamus ante turpis, convallis et ex in, posuere maximus turpis.
        In mattis in dui ac fermentum.
        """),
    ],
    text_align=Text.Align.CENTER,
    paragraph_spacing=1,
)

bullet_widget = Bullets([
    'welcome bullet 1',
    'welcome bullet 2',
    ],
)

welcome_slide = Slide(title='Welcome', widgets=[
    text_widget,
    # Limitation
    # ----------
    # Fails rendering properly ~text_widget comes before bullet_widget. The
    # commit that leads to this is 0753e337ec99ccfb2c867a9fd9dd4c7c61154007
    # which optimizes the rendering of "multi-widget-cleanup" actions.
    [bullet_widget, ~text_widget],
    ~bullet_widget,
])



# ------------------------------------------------------------------------------
# Slide #2

class MovableText(Text):

    async def handle_move(self, **kw):

        for _ in range(10):
            self.window.move(dx=-1)
            await self.render()
            await api.sleep(0.02)
        return 'done'


text = MovableText('content text #1', template_slot='mid')

content_slide = Slide(title='[content]', widgets=[
    text,
    text.request('move'),
    Bullets(['bullet 1', 'bullet 2']),
    Text('content text #3'),
])



# ------------------------------------------------------------------------------
# Slide #3

thanks_slide = Slide(title='Thanks!', widgets=[
    # Overriding template suggested geometry: go big!
    Text('by bye text', geometry=dict(x=0.1, y=0.2, w=0.8, h=0.8, dh=-3)),
])


# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    welcome_slide,
    content_slide,
    thanks_slide,
])

