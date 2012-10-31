"""`ezmlex.tokens`

TODO: Write docs for `ezmlex.tokens` module
"""

#
# Copyright (c) 2012 by Pawel Tomulik
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

__docformat__ = "restructuredText"

class TokenBase(object):

    @classmethod
    def id(cls):
        return cls._id

    @classmethod
    def _set_id(cls, _id):
        cls._id = _id

    @classmethod
    def pattern(cls):
        return cls._pattern

    @classmethod
    def _set_pattern(cls, pattern, *args):
        from ezmlex.patterns import recompile
        cls._pattern = recompile(pattern, *args)
            
    @classmethod
    def match(cls, *args):
        return cls.pattern().match(*args)

    @classmethod
    def is_error(cls):
        return False

    @classmethod
    def message(cls):
        return ''

    def __init__(self, line_no, col_no, char_no):
        self._line_no = line_no
        self._col_no = col_no
        self._char_no = char_no

    def line_no(self):
        return self._line_no

    def col_no(self):
        return self._col_no

    def char_no(self):
        return self._char_no
   
    def value(self):
        return self._value

    def str(self):
        return str(self.value())

    def unicode(self):
        return unicode(self.value())

    def set_value(self, value):
        self._value = value

def def_token(tab, _id, pattern, name=None, *args):
    try: 
        Token = tab[_id]
        raise RuntimeError("token already defined: %r = %r" % (_id, Token))
    except KeyError:
        if name is None: name = _id
        class Token(TokenBase): pass
        Token._set_id(_id)
        Token._set_pattern(pattern, *args)
        Token.__name__ = name + "Token" # for debugging
        tab[_id] = Token

def del_token(tab, _id):
    del tab[_id]

def token(tab, _id):
    return tab[_id]

def find_matching_tokens(tab, *args):
    result = []
    for t_id, t_class in tab.items():
        t_match = t_class.match(*args)
        if t_match:
            result.append((t_id, t_class, t_match))
    return result
     

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
