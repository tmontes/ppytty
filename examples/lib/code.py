
from ppytty import SlideDeck, Slide, SlideTemplate, Text, Code


Text.padding = Code.padding = (1, 2)

SlideTemplate.widgets = [
    Text(
        text='Code Widget Test {slide_number}/{slide_count} | {slide_title}',
        use_context=True,
        geometry=dict(x=0, y=0, w=1.0, h=3),
    )
]

SlideTemplate.widget_slots = {
    'left': dict(x=4, y=0.2, w=0.5, h=0.7, dw=-5),
    'right': dict(x=0.5, y=0.2, w=0.5, h=0.7, dx=1, dw=-5),
}


# ------------------------------------------------------------------------------
# Slide | Basic Code

code = r'''
def add(a, b):
    """
    Returns a plus b.
    """
    return a + b
'''

code_from_str = Code(code=code)
code_from_file = Code(file_name='files/fib.py')

code_basic = Slide(title='Code from str/file', widgets=[[
    code_from_str,
    code_from_file,
]])



# ------------------------------------------------------------------------------
# Slide | Pygments styles builtin and custom


try:
    from pygments import style, token

    class CustomStyle(style.Style):
        styles = {
            token.Comment: '#208080',
            token.Literal.String: '#40a040',
            token.Keyword: '#0080f0',
            token.Operator: '#f000f0',
            token.Name.Function: '#f0a000',
        }
except ImportError:
    CustomStyle = object

code_non_default_style = Code(code='# bw style\n'+code, pygm_style_name='bw')
code_custom_style = Code(code='# custom style\n'+code, pygm_style=CustomStyle)

code_styles = Slide(title='Selected builtin / custom styles', widgets=[[
    code_non_default_style,
    code_custom_style,
]])



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    code_styles,
    code_basic,
])
