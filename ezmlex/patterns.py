"""`ezmlex.patterns`

Pattern tables management for tokenizers.
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

def ccat(*reseq):
    """Concatenate sequence of regular expressions into one.
    
    Example
    """
    import re
    from ezmlex.util import is_string
    result = r''
    for ri in reseq:
        if is_string(ri):
            result += ri
        else:
            try:
                # NOTE: If `ri' is not a string, then we expect it is a
                # compiled regular expression, so it should have `pattern'
                # attribute and it should be a string (if it's not a string,
                # the += operator throws TypeError).
                result += ri.pattern
            except AttributeError, TypeError:
                raise TypeError('not a regular expression: %r' % ri)
    return re.compile(result)

def ccatg(*reseq):
    """Concatenate sequence of regular expressions and enclose into group"""
    import re
    return ccat(r'(?:', ccat(*reseq), r')')

def recompile(regex, *args):
    import re
    from ezmlex.util import is_string
    try: 
        regex = regex.pattern
    except AttributeError:
        if not is_string(regex):
            raise TypeError("not a pattern: %r" % regex)
    return re.compile(regex, *args)

def def_pattern(tab, _id, regex, *args):
    try: 
        p = tab[_id]
        try: 
            pp = p.pattern
            raise RuntimeError("pattern already defined: %r = %r" % (_id, pp))
        except AttributeError:
            raise RuntimeError("pattern already defined: %r = %r" % (_id, p))
    except KeyError:
        tab[_id] = recompile(regex, *args)
      
def del_pattern(tab, _id):
    del tab[_id]

def pattern(tab, _id):
    return tab[_id]

def find_matching_patterns(tab, *args):
    result = []
    for p_id, p_re in tab.items():
        if p_re.match(*args):
            result.append(p_id)
    return result

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
