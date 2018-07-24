
from ppytty import SlideDeck, Slide


ppytty_task = SlideDeck([
    Slide(title='Welcome', widgets=[1]),
    Slide(title='[content]', widgets=[1, 2, 3]),
    Slide(title='Thanks!', widgets=[1]),
])


