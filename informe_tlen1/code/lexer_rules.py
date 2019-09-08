tokens = [
    'IDENTIFIER',
    'STRING',
    'NUMBER',
    'KEY',
    'COMMA',
    'EQUALS',
    'LBRACKET',
    'RBRACKET',
    'LPAREN',
    'RPAREN'
]


def t_error(token):
    message = "Token desconocido:"
    message += "\ntype:" + token.type
    message += "\nvalue:" + str(token.value)
    message += "\nline:" + str(token.lineno)
    message += "\nposition:" + str(token.lexpos)
    raise Exception(message)


t_IDENTIFIER = r'(size|rectangle|line|circle|ellipse|polyline|polygon|text)'
t_STRING = r'\"([^\\\n]|(\\.))*?(?<!\\)"'
t_KEY = r'\w[\w\d_-]*'
t_COMMA = r","
t_EQUALS = r"="
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LPAREN = r"\("
t_RPAREN = r"\)"


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large", t.value)
        t.value = 0
    return t


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'
