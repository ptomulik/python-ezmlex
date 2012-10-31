"""`examples/apidoc/TokenizerBase1.py`

Example usage of `ezmlex.tokenizers.TokenizerBase` class. Decompose text into
words, punctuators and whitespaces. Report errors in input stream.
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


from ezmlex.tokenizers import TokenizerBase
from ezmlex.buffers import CharOrientedBuffer

class Buffer(CharOrientedBuffer):
    @classmethod
    def _make_fsm_str(cls,items):
        return items

class Tokenizer(TokenizerBase):
    def _init_buffer(self, *args, **kw):
        self._buffer = Buffer(*args, **kw)

# Syntax definition for Tokenizer
Tokenizer.def_token_type('Word',        r'[a-zA-Z]+')
Tokenizer.def_token_type('Separator',   r'[ \t\n]+')
Tokenizer.def_token_type('Punctuator',  r'[\.,;:-]')
Tokenizer.def_error_type('SyntaxError', r'[^ \t\n]+', 'syntax error')

# Input string
_input = """Lorem ipsum dolor sit amet, consectetur adipiscing
elit. Sed aliquet odio quis elit aliquet eu interdum justo
adipiscing. #% Vestibulum sodales ornare adipiscing."""

# Tokenizer instance
tokenizer = Tokenizer(_input)

# Recognize tokens
for token in iter(tokenizer):
    if token.is_error():
        print "%d:%d:Error:%s:%r" \
          % (token.line_no(), token.col_no(), token.message(), token.value())
    else:
        print "%d:%d:%s:%r" \
          % (token.line_no(), token.col_no(), token.id(), token.value())

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
