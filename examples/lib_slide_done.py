
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets


Text.padding = Bullets.padding = (1, 2)

SlideTemplate.widgets = [
    Text(text=[
        'Slide Widget Test {slide_number}/{slide_count} | {slide_title}',
    ],
    use_context=True,
    geometry=dict(x=0, y=0, w=1.0, h=3),
    )
]

SlideTemplate.widget_slots = {
    'left': dict(x=0.05, y=0.2, w=0.3, h=0.7, dx=1, dw=-2),
    'center': dict(x=0.35, y=0.2, w=0.3, h=0.7, dx=1, dw=-2),
    'right': dict(x=0.65, y=0.2, w=0.3, h=0.7, dx=1, dw=-2),
}


# ------------------------------------------------------------------------------
# Slide | Done when widgets done

slide_done_when_widgets_done = Slide(title='Done when widgets done', widgets=[
    Text(text=['One']),
    Text(text=['Two']),
    Bullets(items='one two three'.split())
])



# ------------------------------------------------------------------------------
# Slide | Not done when widgets done

slide_running_when_widgets_done = Slide(title='Running when widgets done', widgets=[
    Text(text=['One']),
    Text(text=['Two']),
    Bullets(items='one two three'.split())
], ever_done=False)



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    slide_done_when_widgets_done,
    slide_running_when_widgets_done,
    Slide(title='Empty never done', ever_done=False),
    Slide(title='Empty default'),
    Slide(title="Last Slide to confirm the previous one's behaviour"),
])
