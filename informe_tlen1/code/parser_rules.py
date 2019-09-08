required = {
    'size': {
        'height': int,
        'width': int
    },
    'rectangle': {
        'upper_left': (int, int),
        'height': int,
        'width': int
    },
    'line': {
        'from': (int, int),
        'to': (int, int)
    },
    'circle': {
        'center': (int, int),
        'radius': int
    },
    'ellipse': {
        'center': (int, int),
        'rx': int,
        'ry': int
    },
    'polyline': {
        'points': [(int, int)]
    },
    'polygon': {
        'points': [(int, int)]
    },
    'text': {
        't': str,
        'at': (int, int)
    }
}

optional = {
    'text': {
        'font-family': str,
        'font-size': str
    }
}

common = {
    'fill': str,
    'stroke': str,
    'stroke-width': int
}


class SemanticException(Exception):
    pass


def type_assert(a, b):
    if type(b) == tuple:
        if type(a) is not tuple:
            return False

        for x, y in zip(a, b):
            if not isinstance(x, y):
                return False

        return True
    elif type(b) == list:
        if type(a) is not list:
            return False

        b = b[0]
        for entry in a:
            if not type_assert(entry, b):
                return False

        return True
    else:
        return isinstance(a, b)


def p_statement(subexpressions):
    '''statement : expression
                 | statement expression'''

    if len(subexpressions) == 3:
        subexpressions[0] = [subexpressions[2]]
        subexpressions[0] += subexpressions[1]

        if subexpressions[2][0] == 'size':
            for entry in subexpressions[1]:
                if entry[0] == 'size':
                    raise SemanticException("Line {}: Size defined twice.".format(subexpressions.lexer.lineno))
    else:
        subexpressions[0] = [subexpressions[1]]


def p_expression(subexpressions):
    'expression : IDENTIFIER key_value_list'
    subexpressions[0] = (subexpressions[1], subexpressions[2])

    (identifier, arguments) = subexpressions[0]

    unmet_requirements = []
    for key in required[identifier]:
        if key not in arguments:
            unmet_requirements.append(key)

    if len(unmet_requirements) > 0:
        raise SemanticException(
            "Line {}: Parameters {} need to be defined for {}".format( subexpressions.lexer.lineno - 1, unmet_requirements, identifier))

    # Check types and key validity
    for key in arguments:
        if key in common:
            if type_assert(arguments[key], common[key]):
                return
            raise SemanticException(
                "Line {}: Type of parameter {} for {} is {}, not {}".format( subexpressions.lexer.lineno - 1, key, identifier, common[key], arguments[key]))
        elif key in required[identifier]:
            if type_assert(arguments[key], required[identifier][key]):
                return
            raise SemanticException(
                "Line {}: Type of parameter {} for {} is {}, not {}".format( subexpressions.lexer.lineno - 1, key, identifier, required[key], arguments[key]))
        elif identifier in optional and key in optional[identifier]:
            if type_assert(arguments[key], optional[identifier][key]):
                return
            raise SemanticException(
                "Line {}: Type of parameter {} for {} is {}, not {}".format( subexpressions.lexer.lineno - 1, key, identifier, optional[identifier][key], arguments[key]))
        else:
            raise SemanticException(
                "Line {}: Unknown parameter {} for {}.".format( subexpressions.lexer.lineno - 1, key, identifier))


def p_key_value_list(subexpressions):
    '''key_value_list : key_value_entry COMMA key_value_list
                      | key_value_entry
    '''

    kv = subexpressions[1]

    if len(subexpressions) == 4:
        for key in subexpressions.slice[3].value:
            if key in kv:
                raise SemanticException('Double definition for key {}'.format(key))
        kv.update(subexpressions.slice[3].value)

    subexpressions[0] = kv


def p_key_value_entry(subexpressions):
    'key_value_entry : KEY EQUALS value'
    subexpressions[0] = {
        subexpressions[1]: subexpressions[3]
    }


def p_value(subexpressions):
    '''value : STRING
             | NUMBER
             | LPAREN value COMMA value RPAREN
             | LBRACKET array RBRACKET'''

    if subexpressions.slice[1].type == 'STRING':
        subexpressions[0] = str(subexpressions.slice[1].value)[1:-1]
    elif subexpressions.slice[1].type == 'NUMBER':
        subexpressions[0] = int(subexpressions.slice[1].value)
    elif subexpressions.slice[1].type == 'LPAREN':
        subexpressions[0] = (subexpressions[2], subexpressions[4])
    elif subexpressions.slice[1].type == 'LBRACKET':
        subexpressions[0] = subexpressions[2]


def p_array(subexpressions):
    '''array : value
             | value COMMA array'''

    subexpressions[0] = [subexpressions[1]]

    if len(subexpressions) == 4:
        subexpressions[0] += subexpressions[3]


def p_error(token):
    message = "[Syntax error]"
    if token is not None:
        message += "\ntype:" + token.type
        message += "\nvalue:" + str(token.value)
        message += "\nline:" + str(token.lineno)
        message += "\nposition:" + str(token.lexpos)
    raise Exception(message)
