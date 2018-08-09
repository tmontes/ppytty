
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
# Slide | Bullet Delivery Variations

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
# Slide | Bullet Types

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
callable_bullets = Bullets(items=bullet_items, at_once=True, bullets=(
                            Bullets.numbers(fmt='b'), # Binary, why not?!... :)
                            Bullets.letters,
                            ),
                           )

bullet_types = Slide(title='Bullet Types', widgets=[[
    default_bullets,
    custom_bullets,
    callable_bullets,
]])



# ------------------------------------------------------------------------------
# Slide | Properly wrap long item text.

bullet_items = [
    'Short item text.',
    'Long item: The quick brown fox jumped over the lazy dog.',
    'Sub items here:', [
        'Short sub A',
        'Short sub B',
        'Much longer sub C, which needs to wrap too.',
    ],
    'Pretty much done!'
]

bullets_with_long_items = Bullets(items=bullet_items, at_once=True)
too_many_bullets = Bullets(items=[f'Item {n}' for n in range(20)], at_once=True)
too_many_too_long = Bullets(items=bullet_items*3, at_once=True)

bullet_item_wrapping = Slide(title='Bullet Item Text Wrapping', widgets=[[
    bullets_with_long_items,
    too_many_bullets,
    too_many_too_long
]])



# ------------------------------------------------------------------------------
# Slide | Post item/item-group spacing.

bullet_items = [
    'Item A',
    'Item B', [
        'Sub 1',
        'Sub 2',
        'Sub 3',
    ],
    'Item C', [
        'Sub 1 which is actually pretty long.',
        'Sub 2 is also pretty long and forces wrapping...',
    ],
    'Pretty much done!'
]

bullets_no_spacing = Bullets(items=bullet_items, at_once=True)
bullets_spacing_outer = Bullets(items=bullet_items, at_once=True, spacing=(1, 0))
bullets_spacing_inner = Bullets(items=bullet_items, at_once=True, spacing=(0, 1))

bullet_item_spacing = Slide(title='Post Item/Item-group Spacing', widgets=[[
    bullets_no_spacing,
    bullets_spacing_outer,
    bullets_spacing_inner,
]])



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    bullet_item_spacing,
    bullet_item_wrapping,
    bullet_types,
    bullet_delivery,
])
