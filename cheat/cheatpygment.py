import os

from pygments.lexer import RegexLexer
from pygments.style import Style
from pygments.token import *
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter

class CheatLexer(RegexLexer):
	name = 'Cheat'
	aliases = ['cheat', 'cheatsheet']
	filenames = []

	tokens = {
		'root': [
			(r'#.*\n', String),
			(r'.*\n', Comment),
		]
	}

class CheatStyle(Style):
	styles = {
		String:		'#ansired',
		Comment:	'#ansiblue',
	}



def colorize(sheet_content):
    """ Colorizes cheatsheet content if so configured """

    # only colorize if so configured
    if not 'CHEATCOLORS' in os.environ:
        return sheet_content

    # use CheatPygment by default
    lexer     	= CheatLexer()
    style 		= CheatStyle

    # use other lexer if specified
    first_line	= sheet_content.splitlines()[0]
    if first_line.startswith('```'):
        sheet_content = '\n'.join(sheet_content.split('\n')[1:-2])
        try:
            lexer = get_lexer_by_name(first_line[3:])
            style = 'default'
        except Exception:
            pass

    return highlight(sheet_content, lexer, Terminal256Formatter(style=style))
