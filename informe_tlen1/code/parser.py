import ply.yacc as yacc
import ply.lex as lex
from .lexer_rules import *
from .parser_rules import *


def parse(text, debug=False):
    lexer = lex.lex(debug=debug)
    parser = yacc.yacc(method='SLR', debug=debug)
    document = parser.parse(text, lexer)

    canvas = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'
    shapes = []

    for key, value in reversed(document):
        if key == 'size':
            canvas = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{}" height="{}">'.format(value['width'], value['height'])
            continue
        if key == 'rectangle':
            element = '<rect x="{}" y="{}" height="{}" width="{}"'.format(
                value['upper_left'][0],
                value['upper_left'][1],
                value['height'],
                value['width']
            )
        elif key == 'line':
            element = '<line x1="{}" y1="{}" x2="{}" y2="{}"'.format(
                value['from'][0],
                value['from'][1],
                value['to'][0],
                value['to'][1]
            )
        elif key == 'circle':
            element = '<circle cx="{}" cy="{}" r="{}"'.format(
                value['center'][0],
                value['center'][1],
                value['radius']
            )
        elif key == 'ellipse':
            element = '<ellipse cx="{}" cy="{}" rx="{}" ry="{}"'.format(
                value['center'][0],
                value['center'][1],
                value['rx'],
                value['ry']
            )
        elif key == 'polyline':
            element = '<polyline points="{}"'.format(
                " ".join(["{},{}".format(point[0], point[1]) for point in value['points']])
            )
        elif key == 'polygon':
            element = '<polygon points="{}"'.format(
                " ".join(["{},{}".format(point[0], point[1]) for point in value['points']])
            )
        elif key == 'text':
            element = '<text x="{}" y="{}"'.format(
                value['at'][0],
                value['at'][1]
            )
            if 'font-family' in value:
                element += ' font-family="{}"'.format(value['font-family'])
            if 'font-size' in value:
                element += ' font-size="{}"'.format(value['font-size'])
        for par in common:
            if par in value:
                element += ' {}="{}"'.format(
                    par,
                    value[par]
                )
        if key == 'text':
            element += '>{}</text>'.format(value['t'])
        else:
            element += '/>'
        shapes.append(element)
    return "{}{}</svg>".format(canvas, "".join(shapes))
