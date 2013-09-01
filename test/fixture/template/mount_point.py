# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import lucidity


def register():
    '''Register templates.'''
    return [
        lucidity.Template('a', '/a/pattern'),
        lucidity.Template('b', '/b/pattern')
    ]
