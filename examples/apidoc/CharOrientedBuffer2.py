"""`examples/apidoc/CharOrientedBuffer2.py`

Example usage of `ezmlex.buffers.CharOrientedBuffer` class. Read words from
input, treat all other tokens as errors.
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

import re
from ezmlex.buffers import CharOrientedBuffer
class Buffer(CharOrientedBuffer):
    @classmethod
    def _make_fsm_str(cls,items):
        return items
txt = """Lorem ipsum dolor sit amet, consectetur adipiscing
elit. Sed aliquet odio quis elit aliquet eu interdum justo
adipiscing. Vestibulum sodales ornare adipiscing."""
buf = Buffer(txt)
word = re.compile(r'[a-zA-Z]+')
sep = re.compile(r'[ \t\n]+')
eoi = (buf.extend(32) < 32)
while len(buf):
    wm = word.match(buf.fsm_str())
    sm = sep.match(buf.fsm_str())
    if wm:
        if len(wm.group(0)) < len(buf) or eoi:
            # entire word recognized, shift it out from the buffer and
            # print it out
            s = buf.shift(len(wm.group(0)))
            print "%d:%d:word:%r" % (s.line_no(), s.col_no(), s.__str__())
        else:
            # read more characters to recover entire word
            eoi = (buf.extend(32) < 32)
    elif sm:
        # just shift out whitespaces
        buf.shift(len(sm.group(0)))
    else:
        print "%d:%d:error:%r" % (buf.line_no(), buf.col_no(), buf[0])
        buf.shift(1)
    if not eoi and len(buf) == 0:
        buf.extend(32)

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
