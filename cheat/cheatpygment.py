import os

from pygments.lexer import Lexer, RegexLexer, do_insertions, bygroups, \
    include, default, this, using, words
from pygments.token import Punctuation, \
    Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.util import shebang_matches

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
				include('basic'),
				(r'`', String.Backtick, 'backticks'),
				include('data'),
				include('interp'),
			],
			'interp': [
				(r'\$\(\(', Keyword, 'math'),
				(r'\$\(', Keyword, 'paren'),
				(r'\$\{#?', String.Interpol, 'curly'),
				(r'\$[a-zA-Z_]\w*', Name.Variable),  # user variable
				(r'\$(?:\d+|[#$?!_*@-])', Name.Variable),      # builtin
				(r'\$', Text),
			],
			'basic': [
				(r'\b(if|fi|else|while|do|done|for|then|return|function|case|'
				 r'select|continue|until|esac|elif)(\s*)\b',
				 bygroups(Keyword, Text)),
				(r'\b(alias|bg|bind|break|builtin|caller|cd|command|compgen|'
				 r'complete|declare|dirs|disown|echo|enable|eval|exec|exit|'
				 r'export|false|fc|fg|getopts|hash|help|history|jobs|kill|let|'
				 r'local|logout|popd|printf|pushd|pwd|read|readonly|set|shift|'
				 r'shopt|source|suspend|test|time|times|trap|true|type|typeset|'
				 r'ulimit|umask|unalias|unset|wait)(?=[\s)`])',
				 Name.Builtin),
				(r'\A#!.+\n', Comment.Hashbang),
				(r'#.*\n', Comment.Single),
				(r'\\[\w\W]', String.Escape),
				(r'(\b\w+)(\s*)(\+?=)', bygroups(Name.Variable, Text, Operator)),
				(r'[\[\]{}()=]', Operator),
				(r'<<<', Operator),  # here-string
				(r'<<-?\s*(\'?)\\?(\w+)[\w\W]+?\2', String),
				(r'&&|\|\|', Operator),
			],
			'data': [
				(r'(?s)\$?"(\\\\|\\[0-7]+|\\.|[^"\\$])*"', String.Double),
				(r'"', String.Double, 'string'),
				(r"(?s)\$'(\\\\|\\[0-7]+|\\.|[^'\\])*'", String.Single),
				(r"(?s)'.*?'", String.Single),
				(r';', Punctuation),
				(r'&', Punctuation),
				(r'\|', Punctuation),
				(r'\s+', Text),
				(r'\d+\b', Number),
				(r'[^=\s\[\]{}()$"\'`\\<&|;]+', Text),
				(r'<', Text),
			],
			'string': [
				(r'"', String.Double, '#pop'),
				(r'(?s)(\\\\|\\[0-7]+|\\.|[^"\\$])+', String.Double),
				include('interp'),
			],
			'curly': [
				(r'\}', String.Interpol, '#pop'),
				(r':-', Keyword),
				(r'\w+', Name.Variable),
				(r'[^}:"\'`$\\]+', Punctuation),
				(r':', Punctuation),
				include('root'),
			],
			'paren': [
				(r'\)', Keyword, '#pop'),
				include('root'),
			],
			'math': [
				(r'\)\)', Keyword, '#pop'),
				(r'[-+*/%^|&]|\*\*|\|\|', Operator),
				(r'\d+#\d+', Number),
				(r'\d+#(?! )', Number),
				(r'\d+', Number),
				include('root'),
			],
			'backticks': [
				(r'`', String.Backtick, '#pop'),
				include('root'),
			],
		}

	def analyse_text(text):
		if shebang_matches(text, r'(ba|z|)sh'):
			return 1
		if text.startswith('$ '):
			return 0.2


# Bold colors:
# darkgray, red, green, yellow, fuchsia, turquoise, white

# Light colors:
# black, darkred, darkgreen, brown, darkblue, purple, teal, lightgray

class CheatStyle(Style):
	styles = {
		String:		'#ansibrown',
		Comment:	'#ansiteal',
		Operator:		'#ansired',
		Keyword:	'#ansiwhite',
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

	print('lexer =', lexer, 'style =', style)
	return highlight(sheet_content, lexer, Terminal256Formatter(style=style))
