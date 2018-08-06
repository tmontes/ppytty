
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Bullets


Text.padding = Bullets.padding = (1, 2)

SlideTemplate.widgets = [
    Text(text=[
        'Bullets Widget Tests | {slide_title}',
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
# Slide #1

bullet_items = [
    'Colours',
    ['red', 'green', 'blue'],
    'Workdays',
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
]

bullets_at_once = Bullets(items=bullet_items, at_once=True)
bullets_by_group = Bullets(items=bullet_items, at_once=(False, True))
bullets_by_item = Bullets(items=bullet_items, at_once=False)

bullet_delivery = Slide(title='Bullet Delivery', widgets=[
    bullets_at_once,
    bullets_by_group,
    bullets_by_item,
])



# ------------------------------------------------------------------------------
# Slide #2

bullet_items = [
    'Colours',
    ['red', 'green', 'blue'],
    'Workdays',
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'Three',
    'Four',
    'Five',
    'Six',
    'Seven',
    'Eight',
    'Nine',
    'Ten',
]

default_bullets = Bullets(items=bullet_items, at_once=True)
custom_bullets = Bullets(items=bullet_items, at_once=True, bullets=('* ', '> '))

arabic_bullets = lambda n: f'{n}. '
letter_bullets = lambda n: chr(n - 1 + ord('a')) + '. '

callable_bullets = Bullets(items=bullet_items, at_once=True, bullets=(arabic_bullets, letter_bullets))

bullet_types = Slide(title='Bullet Types', widgets=[
    default_bullets,
    custom_bullets,
    callable_bullets,
])



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    bullet_delivery,
    bullet_types,
])
