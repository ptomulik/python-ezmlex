"""`CharOrientedBuffer1.py`

Example usage of `ezmlex.buffers.CharOrientedBuffer` class. Read chunks of 
32 characters and output chunks of 8 characters.
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


from ezmlex.buffers import CharOrientedBuffer
class Buffer(CharOrientedBuffer):
    @classmethod
    def _make_fsm_str(cls,items):
        return items
txt = """Lorem ipsum dolor sit amet, consectetur adipiscing
elit. Sed aliquet odio quis elit aliquet eu interdum justo
adipiscing. Vestibulum sodales ornare adipiscing."""
buf = Buffer(txt)
while buf.extend(32):
    while 8 <= len(buf):
        s = buf.shift(8)
        print "%d:%d:%r" % (s.line_no(), s.col_no(), s.__str__())
if len(buf):
    # Print out remaining part of text (a tail shorter than 8 chars)
    print "%d:%d:%r" % (buf.line_no(), buf.col_no(), buf.__str__())

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
