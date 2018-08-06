
from ppytty import SlideDeck, Slide, SlideTemplate, Bullets


SlideTemplate.widget_slots = {
    'left': dict(x=0.05, y=0.2, w=0.3, h=0.6, dx=1, dw=-2),
    'center': dict(x=0.35, y=0.2, w=0.3, h=0.6, dx=1, dw=-2),
    'right': dict(x=0.65, y=0.2, w=0.3, h=0.6, dx=1, dw=-2),
}

Bullets.padding = (1, 2)


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

bullet_delivery = Slide(title='Welcome', widgets=[
    bullets_at_once,
    bullets_by_group,
    bullets_by_item,
])



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    bullet_delivery,
])
