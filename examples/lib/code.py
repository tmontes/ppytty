
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
# Slide | Long-line handling

code = r'''
# This is a single-line, very long comment, that does not to fit in a single output line.
def incredible_function(operation, *arguments, **options):
    """
    Returns a plus b.
    """
    return a + b
'''

code_long_lines_wrap = Code(code=code, wrap=True)
code_long_lines_trunc = Code(code=code, wrap=False)

code_long_lines = Slide(title='Long line wrapping/truncating', widgets=[[
    code_long_lines_wrap,
    code_long_lines_trunc,
]])



# ------------------------------------------------------------------------------
# Slide | Long code truncation

code = r'''
my_long_dict = {
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 1,
    11: 1,
    12: 1,
    13: 1,
    13: 1,
    14: 1,
    15: 'This is a very long string forcing the output window to do wrapping.',
    16: 1,
    17: 1,
    18: 1,
    19: 1,
    20: 1,
}
'''

code_long_truncate = Code(code=code, wrap=True)
code_long_offset = Code(code=code, wrap=False)

code_long = Slide(title='Long code truncation', widgets=[[
    code_long_truncate,
    code_long_offset,
]])



# ------------------------------------------------------------------------------
# Slide | Line numbers and long-line handling

code = r'''
# This is a single-line, very long comment, that does not to fit in a single output line.
def incredible_function(operation, *arguments, **options):
    """
    Returns a plus b.
    """
    return a + b


def another_function():
    """
    Answer to the Ultimate Question of Life, the Universe, and Everything.
    """
    return 42

'''

code_long_lines_wrap_numbered = Code(code=code, wrap=True, padding=(1, 2, 1, 1),
                                     line_numbers=True,
                                     line_number_suffix=' \N{BOX DRAWINGS LIGHT VERTICAL} ')
code_long_lines_trunc_numbered = Code(code=code, wrap=False, padding=(1, 2, 1, 1),
                                      line_numbers=True, line_number_fmt='02x',
                                      line_number_fg=248, line_number_bg=242)

code_long_lines_numbered = Slide(title='Line numbers and long line wrap/truncate', widgets=[[
    code_long_lines_wrap_numbered,
    code_long_lines_trunc_numbered,
]])



# ------------------------------------------------------------------------------
# The SlideDeck

ppytty_task = SlideDeck([
    code_long_lines_numbered,
    code_long,
    code_long_lines,
    code_styles,
    code_basic,
])
