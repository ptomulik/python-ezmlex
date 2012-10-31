# coding: utf-8
""" debian_control_tests.parsing.test_buffers

Unit tests for ezmlex.buffers module
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


from unittest import TestCase
from mock import Mock, MagicMock, patch
from ezmlex.buffers import TokenizerBufferBase
from ezmlex.buffers import CharOrientedBuffer
from ezmlex.buffers import LineOrientedBuffer

#############################################################################
# Test some simple calls to TokenizerBufferBase's methods. For each invocation
# only a minimal set of (normally abstract) methods in TokenizerBufferBase is
# defined. We do this by temporarily patching the TokenizerBufferBase class.
# These tests are intended to catch any changes in TokenizerBufferBase that
# could potentially break derived classes.
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::__init__(...) 
#############################################################################
@patch.object(TokenizerBufferBase,'_do_assign')
@patch.object(TokenizerBufferBase,'_update_end_marker')
class Test_TokenizerBufferBase___init__(TestCase):

    @patch.object(TokenizerBufferBase,'bind')
    def test_init_calls_bind_1(self, bind, *args):
        "TokenizerBufferBase() invokes TokenizerBufferBase.bind(None)"
        TokenizerBufferBase()
        bind.assert_called_once_with(None)

    @patch.object(TokenizerBufferBase,'bind')
    def test_init_calls_bind_2(self, bind, *args):
        "TokenizerBufferBase(_input) invokes " \
        "TokenizerBufferBase.bind(_input)"""
        _input = "string input"
        TokenizerBufferBase(_input)
        bind.assert_called_once_with(_input)

    @patch.object(TokenizerBufferBase,'assign')
    def test_init_calls_assign_1(self, assign, *args):
        "TokenizerBufferBase() invokes " \
        "TokenizerBufferBase.assign(0,0,0,None)"""
        TokenizerBufferBase()
        assign.assert_called_once_with(0, 0, 0, None)

    @patch.object(TokenizerBufferBase,'assign')
    def test_init_calls_assign_2(self, assign, *args):
        "TokenizerBufferBase(None,1,2,100,content,key='value') invokes " \
        "TokenizerBufferBase.assert(1,2,100,content,key='value')"""
        content = "string content"
        TokenizerBufferBase(None, 1, 2, 100, content, key='value')
        assign.assert_called_once_with(1, 2, 100, content, key='value')
#############################################################################
    
#############################################################################
# Test: TokenizerBufferBase::bind(...)
#############################################################################
@patch.object(TokenizerBufferBase, '_on_bind')
class Test_TokenizerBufferBase_bind(TestCase):

    @patch.object(TokenizerBufferBase, '_do_assign')
    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def setUp(self, *args):
        self._buffer = TokenizerBufferBase()

    def test_on_bind_called_1(self, _on_bind):
        "TokenizerBufferBase: bind(None) invokes _on_bind(None)"
        self._buffer.bind(None)
        _on_bind.assert_called_once_with(None)

    def test_on_bind_called_2(self, _on_bind):
        "TokenizerBufferBase: bind(\"foo\") invokes _on_bind(\"foo\")"
        self._buffer.bind("foo")
        _on_bind.assert_called_once_with("foo")

    def test_bind_sets__input(self, *args):
        "TokenizerBufferBase: buf._bind(\"foo\") sets " \
        "buf._input = buf._on_bind(\"foo\")"
        with patch.object(TokenizerBufferBase, '_on_bind', 
                          side_effect = lambda x : x):
            self._buffer.bind("input 1")
            self.assertIs(self._buffer._input, "input 1")
            self._buffer.bind("input 2")
            self.assertIs(self._buffer._input, "input 2")
        with patch.object(TokenizerBufferBase, '_on_bind', 
                          side_effect = lambda x : x + " changed"):
            self._buffer.bind("input 3")
            self.assertEqual(self._buffer._input, "input 3 changed")
            self._buffer.bind("input 4")
            self.assertEqual(self._buffer._input, "input 4 changed")
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::set_start_marker(...)
#############################################################################
@patch.object(TokenizerBufferBase, '_update_end_marker')
class Test_TokenizerBufferBase_set_start_marker(TestCase):

    @patch.object(TokenizerBufferBase, '_do_assign')
    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def setUp(self, *args):
        self._buffer = TokenizerBufferBase()

    def test_setstartmarker_sets_marker(self, *args):
        "TokenizerBufferBase: buf.set_start_marker() sets " \
        "buf._<line|col|char>_no"
        self._buffer.set_start_marker(0,0,0)
        self.assertEqual(self._buffer._line_no, 0)
        self.assertEqual(self._buffer._col_no, 0)
        self.assertEqual(self._buffer._char_no, 0)
        self._buffer.set_start_marker(1,2,3)
        self.assertEqual(self._buffer._line_no, 1)
        self.assertEqual(self._buffer._col_no, 2)
        self.assertEqual(self._buffer._char_no, 3)
        
    def test_setstartmarker_calls_updateendmarker(self, _update_end_marker):
        "TokenizerBufferBase: set_start_marker(1,2,3) invokes " \
        "_update_end_marker()"
        self._buffer.set_start_marker(1,2,3)
        _update_end_marker.assert_called_once_with()
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::assign(...)
#############################################################################
@patch.object(TokenizerBufferBase, '_do_assign')
class Test_TokenizerBufferBase_assign(TestCase):

    @patch.object(TokenizerBufferBase, '_do_assign')
    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def setUp(self, *args):
        self._buffer = TokenizerBufferBase()

    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def test_assign_calls_doassign_1(self, _update_end_marker, _do_assign):
        "TokenizerBufferBase: assign(1,2,3,content) invokes " \
        "_do_assign(content)"""
        content = "string content"
        self._buffer.assign(1,2,3, content)
        _do_assign.assert_called_once_with(content)

    @patch.object(TokenizerBufferBase, 'set_start_marker')
    def test_assign_calls_setstartmarker_1(self, set_start_marker, _do_assign):
        "TokenizerBufferBase: assign(1,2,3,content) invokes " \
        "set_start_marker(1,2,3)"""
        content = "string content"
        self._buffer.assign(1,2,3, content)
        set_start_marker.assert_called_once_with(1, 2, 3)
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::extend(...)
#############################################################################
@patch.object(TokenizerBufferBase, '_do_extend')
@patch.object(TokenizerBufferBase, '_update_end_marker')
class Test_TokenizerBufferBase_extend(TestCase):

    @patch.object(TokenizerBufferBase, '_do_assign')
    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def setUp(self, *args):
        self._buffer = TokenizerBufferBase()

    def test_extend_calls_doextend_1(self, _update_end_marker, _do_extend):
        "TokenizerBufferBase: extend() invokes _do_extend(_default_chunk)"
        self._buffer.extend()
        _do_extend.assert_called_once_with(TokenizerBufferBase._default_chunk)

    def test_extend_calls_doextend_2(self, _update_end_marker, _do_extend):
        "TokenizerBufferBase: extend(10) invokes _do_extend(10)"
        self._buffer.extend(10)
        _do_extend.assert_called_once_with(10)

    def test_extend_calls_updateendmarker(self, _update_end_marker, _do_extend):
        "TokenizerBufferBase: extend() invokes _update_end_marker()"
        self._buffer.extend()
        _update_end_marker.assert_called_once_with()
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::shift()
#############################################################################
class Test_TokenizerBufferBase_shift(TestCase):
    
    @patch.object(TokenizerBufferBase, '_do_assign')
    @patch.object(TokenizerBufferBase, '_update_end_marker')
    def setUp(self, *args):
        self._buffer = TokenizerBufferBase()

    def _make_mock_dicts_1(self, content):
        # NOTE: bookmarking values are chosen ad hoc, as they are not
        # important here. The important is that they should differ mutually.
        tb = {  'init'       : Mock(return_value = None), 
                'end_line_no': Mock(return_value = 10),
                'end_col_no' : Mock(return_value = 11),
                'end_char_no': Mock(return_value = 12),
                'getitem'    : Mock(side_effect = lambda i : content[i]) }
        sb = {  'line_no'    : Mock(return_value = 31),
                'col_no'     : Mock(return_value = 32),
                'char_no'    : Mock(return_value = 33),
                'end_line_no': Mock(return_value = 41),
                'end_col_no' : Mock(return_value = 42),
                'end_char_no': Mock(return_value = 43),
                'fsm_str'    : Mock(return_value = content.lower()) }
        return tb, sb

    # Test if buffer object (head) returned by shift() was created with
    # correct arguments (we just check the call to head's __init__())
    def test_shift_calls___init___1(self, *args):
        "TokenizerBufferBase: head = buf.shift(ns) initializes head with " \
        "TokenizerBufferBase(None,buf.line_no(),buf.col_no()," \
        "buf.char_no(),buf[:ns],fsm_str=buf.fsm_str()[:ns])"
        from random import seed,randint,choice
        from string import letters
        seed()
        content = "".join( [choice(letters) for i in xrange(15)])
        TBB = TokenizerBufferBase
        for ns in range(0,len(content)):
            tb, sb = self._make_mock_dicts_1(content)
            with patch.object(TBB, '__init__', tb['init']),\
                 patch.object(TBB, 'end_line_no', tb['end_line_no']), \
                 patch.object(TBB, 'end_col_no', tb['end_col_no']), \
                 patch.object(TBB, 'end_char_no', tb['end_char_no']), \
                 patch.object(TBB, '__getitem__', tb['getitem']),\
                 patch.object(TBB, 'assign'), \
                 patch.object(self._buffer, 'line_no', sb['line_no']),\
                 patch.object(self._buffer, 'col_no', sb['col_no']),\
                 patch.object(self._buffer, 'char_no', sb['char_no']),\
                 patch.object(self._buffer, 'end_line_no', sb['end_line_no']),\
                 patch.object(self._buffer, 'end_col_no', sb['end_col_no']),\
                 patch.object(self._buffer, 'end_char_no', sb['end_char_no']),\
                 patch.object(self._buffer, 'fsm_str', sb['fsm_str']),\
                 patch.object(self._buffer, 'assign'):
                head = self._buffer.shift(ns)
                head.__init__.assert_called_once_with(None,
                    self._buffer.line_no(), self._buffer.col_no(),
                    self._buffer.char_no(), self._buffer[:ns], fsm_str =
                    self._buffer.fsm_str()[:ns])

    # Test if the buffer is re-assigned() with correct arguments during shift()
    def test_shift_calls_assign_1(self, *args):
        "TokenizerBufferBase: head = buf.shift(ns) re-assigns buf with " \
        "buf.assign(head.end_line_no(),head.end_col_no()," \
        "head.end_char_no(),buf[ns:],fsm_str = buf.fsm_str()[ns:])"
        from random import seed,randint,choice
        from string import letters
        seed()
        content = "".join( [choice(letters) for i in xrange(15)])
        TBB = TokenizerBufferBase
        for ns in range(0,len(content)):
            tb, sb = self._make_mock_dicts_1(content)
            with patch.object(TBB, 'end_line_no', tb['end_line_no']), \
                 patch.object(TBB, 'end_col_no', tb['end_col_no']), \
                 patch.object(TBB, 'end_char_no', tb['end_char_no']), \
                 patch.object(TBB, '__getitem__', tb['getitem']),\
                 patch.object(TBB, 'assign'), \
                 patch.object(self._buffer, 'line_no', sb['line_no']),\
                 patch.object(self._buffer, 'col_no', sb['col_no']),\
                 patch.object(self._buffer, 'char_no', sb['char_no']),\
                 patch.object(self._buffer, 'end_line_no', sb['end_line_no']),\
                 patch.object(self._buffer, 'end_col_no', sb['end_col_no']),\
                 patch.object(self._buffer, 'end_char_no', sb['end_char_no']),\
                 patch.object(self._buffer, 'fsm_str', sb['fsm_str']),\
                 patch.object(self._buffer, 'assign'):
                head = self._buffer.shift(ns)
                self._buffer.assign.assert_called_once_with(head.end_line_no(),
                    head.end_col_no(), head.end_char_no(), self._buffer[ns:], 
                    fsm_str = self._buffer.fsm_str()[ns:])
#############################################################################

#############################################################################
# Test: TokenizerBufferBase::[end_]<line|char|col>_no()
#############################################################################
@patch.object(TokenizerBufferBase, '__init__', return_value = None)
class Test_TokenizerBufferBase_bookmarking_accessors(TestCase):
    def test_line_no(self,*args):
        "TokenizerBufferBase: buf.line_no() returns buf._line_no"
        buf = TokenizerBufferBase()
        for buf._line_no in [0, 1, 10]:
            self.assertIs(buf.line_no(), buf._line_no)
    def test_col_no(self,*args):
        "TokenizerBufferBase: buf.col_no() returns buf._col_no"
        buf = TokenizerBufferBase()
        for buf._col_no in [0, 1, 10]:
            self.assertIs(buf.col_no(), buf._col_no)
    def test_char_no(self,*args):
        "TokenizerBufferBase: buf.char_no() returns buf._char_no"
        buf = TokenizerBufferBase()
        for buf._char_no in [0, 1, 10]:
            self.assertIs(buf.char_no(), buf._char_no)
    def test_end_line_no(self,*args):
        "TokenizerBufferBase: buf.end_line_no() returns buf._end_line_no"
        buf = TokenizerBufferBase()
        for buf._end_line_no in [0, 1, 10]:
            self.assertIs(buf.end_line_no(), buf._end_line_no)
    def test_end_col_no(self,*args):
        "TokenizerBufferBase: buf.end_col_no() returns buf._end_col_no"
        buf = TokenizerBufferBase()
        for buf._end_col_no in [0, 1, 10]:
            self.assertIs(buf.end_col_no(), buf._end_col_no)
    def test_end_char_no(self,*args):
        "TokenizerBufferBase: buf.end_char_no() returns buf._end_char_no"
        buf = TokenizerBufferBase()
        for buf._end_char_no in [0, 1, 10]:
            self.assertIs(buf.end_char_no(), buf._end_char_no)
#############################################################################

#############################################################################
# Test: TokenizerBufferBase abstract methods
#############################################################################
@patch.object(TokenizerBufferBase, '__init__', return_value = None)
class Test_TokenizerBufferBase_abstract_methods(TestCase):
    def test_abstract_methods(self,*args):
        "TokenizerBufferBase: abstract methods raise NotImplementedError"
        buf = TokenizerBufferBase()
        with self.assertRaises(NotImplementedError): buf.fsm_str()
        with self.assertRaises(NotImplementedError): str(buf)
        with self.assertRaises(NotImplementedError): unicode(buf)
        with self.assertRaises(NotImplementedError): len(buf)
        with self.assertRaises(NotImplementedError): buf[0]
        with self.assertRaises(NotImplementedError): iter(buf)
        with self.assertRaises(NotImplementedError): buf._do_assign('foo')
        with self.assertRaises(NotImplementedError): buf._do_extend(1)
        with self.assertRaises(NotImplementedError): buf._update_end_marker()

    def test_abstract_classmethods(self,*args):
        "TokenizerBufferBase: abstract class methods raise NotImplementedError"
        with self.assertRaises(NotImplementedError): 
            TokenizerBufferBase._make_fsm_str('abc')
#############################################################################


#############################################################################
#
# Test CharOrientedBuffer methods.
#
#############################################################################


#############################################################################
# Test: CharOrientedBuffer::__init__()
#############################################################################
class Test_CharOrientedBuffer___init__(TestCase):

    def test___init___calls_super(self):
        "CharOrientedBuffer: __init__() calls " \
        "TokenizerBufferBase.__init__() with same arguments"
        kw = { 'key1':'val1', 'key1':'val2' }
        for args in [(),(None,), (None,1), (None,1,2), (None,1,2,3),
                     (None,1,2,3,'content'), ('input',1,2,3,'content')]:
            with patch.object(TokenizerBufferBase,'__init__') as super_init:
                buf = CharOrientedBuffer(*args)
                super_init.assert_called_once_with(buf,*args)
            with patch.object(TokenizerBufferBase,'__init__') as super_init:
                buf = CharOrientedBuffer(*args,**kw)
                super_init.assert_called_once_with(buf,*args,**kw)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: bind()
#############################################################################
class Test_CharOrientedBuffer_bind(TestCase):
    def test_bind_equals_super(self):
        "CharOrientedBuffer.bind equals TokenizerBufferBase.bind"
        # NOTE: this is valid until CharOrientedBuffer.bind() is not defined
        self.assertEqual(CharOrientedBuffer.bind, TokenizerBufferBase.bind)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: set_start_marker()
#############################################################################
class Test_CharOrientedBuffer_set_start_marker(TestCase):
    def test_setstartmarker_equals_super(self):
        "CharOrientedBuffer.set_start_marker() equals " \
        "TokenizerBufferBase.set_start_marker()"
        # If set_start_marker() behaves identically as in TokenizerBufferBase,
        # then it is enough to test _update_end_marker() later.
        self.assertEqual(CharOrientedBuffer.set_start_marker,
                         TokenizerBufferBase.set_start_marker)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: assign()
#############################################################################
class Test_CharOrientedBuffer_assign(TestCase):
    def test_assign_equals_super(self):
        "CharOrientedBuffer.assign equals TokenizerBufferBase.assign"
        # NOTE: this is valid until CharOrientedBuffer.assign() is not defined
        self.assertEqual(CharOrientedBuffer.assign, TokenizerBufferBase.assign)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: extend()
#############################################################################
class Test_CharOrientedBuffer_extend(TestCase):
    def test_extend_equals_super(self):
        "CharOrientedBuffer.extend equals TokenizerBufferBase.extend"
        # NOTE: this is valid until CharOrientedBuffer.extend() is not defined
        self.assertEqual(CharOrientedBuffer.extend, TokenizerBufferBase.extend)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: shift()
#############################################################################
class Test_CharOrientedBuffer_shift(TestCase):
    def test_shift_equals_super(self):
        "CharOrientedBuffer.shift equals TokenizerBufferBase.shift"
        # NOTE: this is valid until CharOrientedBuffer.shift() is not defined
        self.assertEqual(CharOrientedBuffer.shift, TokenizerBufferBase.shift)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: bookmarking()
#############################################################################
class Test_CharOrientedBuffer_bookmarking(TestCase):
    def test_bookmarking_equals_super(self):
        "CharOrientedBuffer.[end_]<line|col|char>_no equals to " \
        "TokenizerBufferBase.[end_]<line|col|char>_no"
        self.assertEqual(CharOrientedBuffer.line_no, 
                         TokenizerBufferBase.line_no)
        self.assertEqual(CharOrientedBuffer.col_no, 
                         TokenizerBufferBase.col_no)
        self.assertEqual(CharOrientedBuffer.char_no, 
                         TokenizerBufferBase.char_no)
        self.assertEqual(CharOrientedBuffer.end_line_no, 
                         TokenizerBufferBase.end_line_no)
        self.assertEqual(CharOrientedBuffer.end_col_no, 
                         TokenizerBufferBase.end_col_no)
        self.assertEqual(CharOrientedBuffer.end_char_no, 
                         TokenizerBufferBase.end_char_no)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: fsm_str()
#############################################################################
class Test_CharOrientedTokenizer_fsm_str(TestCase):
    @patch.object(CharOrientedBuffer, '__init__', return_value = None)
    def test_fsmstr_1(self,*args):
        "CharOrientedBuffer: buf.fsm_str() returns buf._fsm_str"
        buf = CharOrientedBuffer()
        for buf._fsm_str in [ None, '', 'text' ]:
            self.assertIs(buf.fsm_str(), buf._fsm_str)
        # TODO: unicode? 
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: __str__()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
class Test_CharOrientedBuffer___str__(TestCase):
    def test___str___returns__content(self,*args):
        "CharOrientedBuffer: str(buf) returns buf._content"
        buf = CharOrientedBuffer()
        for buf._content in [ '', 'text' ]:
            self.assertIs(str(buf), buf._content)
        # TODO: test on real unicode strings? 
#############################################################################
        
#############################################################################
# Test: CharOrientedBuffer: __unicode__()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
class Test_CharOrientedBuffer___unicode__(TestCase):
    def test___unicode___returns__content(self,*args):
        "CharOrientedBuffer: buf.__unicode__() returns buf._content"
        buf = CharOrientedBuffer()
        for buf._content in [ None, '', 'text' ]:
            self.assertIs(buf.__unicode__(), buf._content)
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: __len__()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer___len__(TestCase):
    def test___len___returns__lencontent(self,*args):
        "CharOrientedBuffer: len(buf) returns len(buf._content)"
        buf = CharOrientedBuffer()
        for _content in [ None, '', 'text' ]:
            buf._do_assign(_content)
            self.assertIs(len(buf), len(buf._content))
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: __getitem__()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer___getitem__(TestCase):
    def test___getitem___returns__contentitem(self,*args):
        "CharOrientedBuffer: buf[i] returns buf._content[i]"
        buf = CharOrientedBuffer()
        for _content in [ None, '', 'text' ]:
            buf._do_assign(_content)
            for i in range(0,len(buf)):
                self.assertEqual(buf[i], buf._content[i])
                self.assertEqual(buf[:i], buf._content[:i])
                self.assertEqual(buf[i:], buf._content[i:])
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: __iter__()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer___iter__(TestCase):
    def test___iter___returns__contentitem(self,*args):
        "CharOrientedBuffer: iter(buf) returns iter(buf._content)"
        buf = CharOrientedBuffer()
        for _content in [ None, '', 'text' ]:
            buf._do_assign(_content)
            self.assertEqual(tuple(iter(buf)), tuple(iter(buf._content)))
        # FIXME: find a better way to verify identity?
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: _on_bind()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
class Test_CharOrientedTokenizer__on_bind(TestCase):
    def test__onbind_sets__doextend_default(self, *args):
        "CharOrientedBuffer: buf._on_bind(None) sets " \
        "buf._do_extend = buf._do_extend_default"
        buf = CharOrientedBuffer()
        self.assertIs(buf._on_bind(None), None)
        self.assertEqual(buf._do_extend, buf._do_extend_default)
    def test__onbind_sets__doextend_string(self, *args):
        "CharOrientedBuffer: buf._on_bind(\"foo\") sets " \
        "buf._do_extend = buf._do_extend_by_string"
        buf = CharOrientedBuffer()
        self.assertIs(buf._on_bind("foo"), "foo")
        self.assertEqual(buf._tell, 0)
        self.assertEqual(buf._do_extend, buf._do_extend_by_string)
    def test__onbind_sets__doextend_by_read(self, *args):
        "CharOrientedBuffer: buf._on_bind(readable) sets " \
        "buf._do_extend = buf._do_extend_by_read"
        class Readable(object):
            def read(self): pass
        buf = CharOrientedBuffer()
        readable = Readable()
        self.assertIs(buf._on_bind(readable), readable)
        self.assertEqual(buf._do_extend, buf._do_extend_by_read)
    def test__onbind_sets__doextend_by_iter(self, *args):
        "CharOrientedBuffer: buf._on_bind(iterable) sets " \
        "buf._do_extend = buf._do_extend_by_iter"
        class Iterable(object):
            def __iter__(self): return iter(['abc','def','ghi'])
        buf = CharOrientedBuffer()
        iterable = Iterable()
        rv = buf._on_bind(iterable)
        self.assertEqual(tuple(rv), tuple(iter(iterable)))
        self.assertEqual(buf._do_extend, buf._do_extend_by_iter)
#############################################################################
        
#############################################################################
# Test: CharOrientedBuffer: _do_assign()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer__do_assign(TestCase):

    def test__doassign_sets_content(self,*args):
        "CharOrientedBuffer: buf._do_assign(\"foo\") sets " \
        "buf._content = \"foo\""
        buf = CharOrientedBuffer()
        for content in ['content', 'other content']:
            buf._do_assign(content)
            self.assertIs(buf._content,content)

    def test__doassign_calls_makefsmstr(self,*args):
        "CharOrientedBuffer: _do_assign() invokes _make_fsm_str"
        buf = CharOrientedBuffer()
        for content in ['content', 'other content']:
            with patch.object(CharOrientedBuffer, '_make_fsm_str', 
                side_effect = lambda x : x) as method:
                buf._do_assign(content)
                method.assert_called_once_with(content)

    def test__doassign_updates_fsmstr(self,*args):
        "CharOrientedBuffer: buf._do_assign(...) updates buf._fsm_str"
        buf = CharOrientedBuffer()
        for content in ['content', 'other content']:
            buf._do_assign(content)
            self.assertEqual(buf._content, buf._fsm_str)
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x.lower() ):
            for content in [ 'Sample One', 'SamplE Two' ]:
                buf._do_assign(content)
                self.assertEqual(buf._content.lower(), buf._fsm_str)

    def test__doassign_none2str(self,*args):
        "CharOrientedBuffer: buf._do_assign(None) sets buf._content = \"\""
        buf = CharOrientedBuffer()
        buf._do_assign(None)
        self.assertIsNot(buf._content,None)
        self.assertIs(buf._content,'')
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: _do_extend_by_string()
#############################################################################
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer__do_extend_by_string(TestCase):
    def test__doextendbystring_1(self,*args):
        "CharOrientedBuffer: buf._do_extend_by_string() works for some " \
        "simple test fixtures"
        _input = '0123456789'
        buf = CharOrientedBuffer()
        buf.bind(_input)
        self.assertEqual(buf._do_extend_by_string(3), 3) # full chunk
        self.assertEqual(buf[:], _input[:len(buf)])
        self.assertEqual(buf._do_extend_by_string(6), 6) # full chunk
        self.assertEqual(buf[:], _input[:len(buf)])
        self.assertEqual(buf._do_extend_by_string(3), 1) # tail
        self.assertEqual(buf[:], _input[:len(buf)])

    def test__doextendbystring_calls_makefsmstr(self,*args):
        "CharOrientedBuffer: _do_extend_by_string() invokes _make_fsm_str()"
        _input = '0123456789'
        buf = CharOrientedBuffer()
        buf.bind(_input)
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_string(3)
            method.assert_called_once()
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_string(6)
            method.assert_called_once()
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_string(3)
            method.assert_called_once()
            
    def test__doextendbystring_updates_fsmstr(self,*args):
        "CharOrientedBuffer: buf._do_extend_by_string() updates buf._fsm_str"
        _input = '0123456789'
        buf = CharOrientedBuffer()
        buf.bind(_input)
        buf._do_extend_by_string(3)
        self.assertEqual(buf._fsm_str, buf._content)
        buf._do_extend_by_string(6)
        self.assertEqual(buf._fsm_str, buf._content)
        buf._do_extend_by_string(3)
        self.assertEqual(buf._fsm_str, buf._content)

#############################################################################

#############################################################################
# Test: CharOrientedBuffer: _do_extend_by_read()
#############################################################################
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer__do_extend_by_read(TestCase):
    def test__doextendbyread_1(self,*args):
        "CharOrientedBuffer: buf._do_extend_by_read() works for some " \
        "simple test fixtures"
        buf = CharOrientedBuffer()
        # TODO: write this test
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: _do_extend_by_iter()
#############################################################################
@patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
class Test_CharOrientedBuffer__do_extend_by_iter(TestCase):
    def test__doextendbyiter_1(self,*args):
        "CharOrientedBuffer: buf._do_extend_by_iter() works for some " \
        "simple test fixtures"
        _input = [ '012', '345', '678' , '9' ]
        buf = CharOrientedBuffer()
        buf.bind(iter(_input))
        self.assertEqual(buf._do_extend_by_iter(3), 3) # '012'
        self.assertEqual(buf[:], ''.join(_input)[:len(buf)])
        self.assertEqual(buf._do_extend_by_iter(4), 6) # '3456[78]'
        self.assertEqual(buf[:], ''.join(_input)[:len(buf)])
        self.assertEqual(buf._do_extend_by_iter(3), 1) # '9' (tail)
        self.assertEqual(buf[:], ''.join(_input)[:len(buf)])

    def test__doextendbyiter_calls_makefsmstr(self,*args):
        "CharOrientedBuffer: _do_extend_by_iter() invokes _make_fsm_str()"
        _input = [ '012', '345', '678' , '9' ]
        buf = CharOrientedBuffer()
        buf.bind(_input)
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_iter(3)
            method.assert_called_once()
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_iter(4)
            method.assert_called_once()
        with patch.object(CharOrientedBuffer,'_make_fsm_str',
            side_effect = lambda x : x) as method:
            buf._do_extend_by_iter(1)
            method.assert_called_once()
            
    def test__doextendbyiter_updates_fsmstr(self,*args):
        "CharOrientedBuffer: buf._do_extend_by_iter() updates buf._fsm_str"
        _input = [ '012', '345', '678' , '9' ]
        buf = CharOrientedBuffer()
        buf.bind(_input)
        buf._do_extend_by_iter(3)
        self.assertEqual(buf._fsm_str, buf._content)
        buf._do_extend_by_iter(4)
        self.assertEqual(buf._fsm_str, buf._content)
        buf._do_extend_by_iter(1)
        self.assertEqual(buf._fsm_str, buf._content)
#############################################################################

#############################################################################
# Test: CharOrientedBuffer: _update_end_marker()
#############################################################################
@patch.object(CharOrientedBuffer, '__init__', return_value = None)
class Test_CharOrientedBuffer__update_end_marker(TestCase):
    def setUp(self, *args):
        self._fixtures = [ { 
            # char:     0
            # col:      0
            'content': '',
            'markers' : [
                (0,  0,  0, 0,  0,  0),
                (1,  0,  0, 1,  0,  0),
                (0,  1,  0, 0,  1,  0),
                (0,  0,  1, 0,  0,  1),
            ]},
            {
            # char:     0123456789012345678
            # col:      0123456789012345678
            'content': 'single line content',
            'markers' : [
                (0,  0,  0, 0, 19, 19),
                (1,  0,  0, 1, 19, 19),
                (0,  1,  0, 0, 20, 19),
                (0,  0,  1, 0, 19, 20),
            ]},
            {
            # char:      01234567890123456
            # col:        0123456789012345
            'content': '\nfirst line empty',
            'markers' : [
                (0,  0,  0, 1, 16, 17),
                (1,  0,  0, 2, 16, 17),
                (0,  1,  0, 1, 16, 17),
                (0,  0,  1, 1, 16, 18),
            ]},
            {
            # char:     01234567890123456 7
            # col:      01234567890123456
            'content': 'second line empty\n',
            'markers' : [
                (0,  0,  0,  1,  0, 18),
                (1,  0,  0,  2,  0, 18),
                (0,  1,  0,  1,  0, 18),
                (0,  0,  1,  1,  0, 19),
            ]},
            {
            #           01234567 89012345
            #                     0123456
            'content': 'two line\ncontent',
            'markers' : [
                (0,  0,  0,  1,  7, 16),
                (1,  0,  0,  2,  7, 16),
                (0,  1,  0,  1,  7, 16),
                (0,  0,  1,  1,  7, 17),
            ]},
            {
            #           01234567 89012345 6
            #                     0123456 7
            'content': 'two line\ncontent\n',
            'markers' : [
                (0,  0,  0,  2,  0, 17),
                (1,  0,  0,  3,  0, 17),
                (0,  1,  0,  2,  0, 17),
                (0,  0,  1,  2,  0, 18),
            ]},
        ]

    @patch.object(CharOrientedBuffer, '_make_fsm_str', side_effect = lambda x:x)
    def test__updateendmarker_1(self, *args):
        "CharOrientedBuffer: buf._update_end_marker() works for several " \
        "test fixtures"
        buf = CharOrientedBuffer()
        for fix in self._fixtures:
            for markers in fix['markers']:
                buf._do_assign(fix['content'])
                buf._line_no, buf._col_no, buf._char_no = markers[:3]
                buf._end_line_no, buf._end_col_no, buf._end_char_no  \
                  = (buf._line_no, buf._col_no, buf._char_no)
                buf._update_end_marker()
                self.assertEqual(buf._end_line_no, markers[3])
                self.assertEqual(buf._end_col_no, markers[4])
                self.assertEqual(buf._end_char_no, markers[5])
#############################################################################


#############################################################################
#
# Test LineOrientedBuffer methods.
# TODO: Develop
#
#############################################################################

###############################################################################
### Test: LineOrientedBuffer::__init__()
###############################################################################
class Test_LineOrientedBuffer___init__(TestCase):

    def test___init___calls_super(self):
        "LineOrientedBuffer: __init__() calls " \
        "TokenizerBufferBase.__init__() with same arguments"
        kw = { 'key1':'val1', 'key1':'val2' }
        for args in [(),(None,), (None,1), (None,1,2), (None,1,2,3),
                     (None,1,2,3,'content'), ('input',1,2,3,'content')]:
            with patch.object(TokenizerBufferBase,'__init__') as super_init:
                buf = LineOrientedBuffer(*args)
                super_init.assert_called_once_with(buf,*args)
            with patch.object(TokenizerBufferBase,'__init__') as super_init:
                buf = LineOrientedBuffer(*args,**kw)
                super_init.assert_called_once_with(buf,*args,**kw)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: bind()
#############################################################################
class Test_LineOrientedBuffer_bind(TestCase):
    def test_bind_equals_super(self):
        "LineOrientedBuffer.bind equals TokenizerBufferBase.bind"
        # NOTE: this is valid until LineOrientedBuffer.bind() is not defined
        self.assertEqual(LineOrientedBuffer.bind, TokenizerBufferBase.bind)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: set_start_marker()
#############################################################################
class Test_LineOrientedBuffer_set_start_marker(TestCase):
    def test_setstartmarker_equals_super(self):
        "LineOrientedBuffer.set_start_marker() equals " \
        "TokenizerBufferBase.set_start_marker()"
        # If set_start_marker() behaves identically as in TokenizerBufferBase,
        # then it is enough to test _update_end_marker() later.
        self.assertEqual(LineOrientedBuffer.set_start_marker,
                         TokenizerBufferBase.set_start_marker)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: assign()
#############################################################################
class Test_LineOrientedBuffer_assign(TestCase):
    def test_assign_equals_super(self):
        "LineOrientedBuffer.assign equals TokenizerBufferBase.assign"
        # NOTE: this is valid until LineOrientedBuffer.assign() is not defined
        self.assertEqual(LineOrientedBuffer.assign, TokenizerBufferBase.assign)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: extend()
#############################################################################
class Test_LineOrientedBuffer_extend(TestCase):
    def test_extend_equals_super(self):
        "LineOrientedBuffer.extend equals TokenizerBufferBase.extend"
        # NOTE: this is valid until LineOrientedBuffer.extend() is not defined
        self.assertEqual(LineOrientedBuffer.extend, TokenizerBufferBase.extend)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: shift()
#############################################################################
class Test_LineOrientedBuffer_shift(TestCase):
    def test_shift_equals_super(self):
        "LineOrientedBuffer.shift equals TokenizerBufferBase.shift"
        # NOTE: this is valid until LineOrientedBuffer.shift() is not defined
        self.assertEqual(LineOrientedBuffer.shift, TokenizerBufferBase.shift)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: bookmarking()
#############################################################################
class Test_LineOrientedBuffer_bookmarking(TestCase):
    def test_bookmarking_equals_super(self):
        "LineOrientedBuffer.[end_]<line|col|char>_no equal to " \
        "TokenizerBufferBase.[end_]<line|col|char>_no"
        self.assertEqual(LineOrientedBuffer.line_no, 
                         TokenizerBufferBase.line_no)
        self.assertEqual(LineOrientedBuffer.col_no, 
                         TokenizerBufferBase.col_no)
        self.assertEqual(LineOrientedBuffer.char_no, 
                         TokenizerBufferBase.char_no)
        self.assertEqual(LineOrientedBuffer.end_line_no, 
                         TokenizerBufferBase.end_line_no)
        self.assertEqual(LineOrientedBuffer.end_col_no, 
                         TokenizerBufferBase.end_col_no)
        self.assertEqual(LineOrientedBuffer.end_char_no, 
                         TokenizerBufferBase.end_char_no)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: fsm_str()
#############################################################################
class Test_LineOrientedTokenizer_fsm_str(TestCase):
    @patch.object(LineOrientedBuffer, '__init__', return_value = None)
    def test_fsmstr_returns__fsmstr(self,*args):
        "LineOrientedBuffer: buf.fsm_str() returns buf._fsm_str"
        buf = LineOrientedBuffer()
        for buf._fsm_str in [ '', 'FSM STR' ]:
            self.assertIs(buf.fsm_str(), buf._fsm_str)
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: __str__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___str__(TestCase):
    def test___str___returns__content(self,*args):
        "LineOrientedBuffer: str(buf) returns joined buf._content items"
        buf = LineOrientedBuffer()
        for buf._content in [ [], [''], ['',''], ['text'], ['ln 1\n','ln 2'] ]:
            self.assertEqual(str(buf), ''.join(buf._content))
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: __unicode__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___unicode__(TestCase):
    def test___unicode___returns__content(self,*args):
        "LineOrientedBuffer: unicode(buf) returns joined buf._content items"
        buf = LineOrientedBuffer()
        for buf._content in [ [],[''], ['\n',''],['text'],['ln 1\n','ln 2'] ]:
            self.assertEqual(unicode(buf), ''.join(buf._content))
        # TODO: test on real unicode unicodeings? 
#############################################################################
        
#############################################################################
# Test: LineOrientedBuffer: __len__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___len__(TestCase):
    def test___len___returns__lencontent(self,*args):
        "LineOrientedBuffer: len(buf) returns len(buf._content)"
        buf = LineOrientedBuffer()
        for buf._content in [ [],[''], ['\n',''],['text'],['ln 1\n','ln 2'] ]:
            self.assertIs(len(buf), len(buf._content))
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: __getitem__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___getitem__(TestCase):
    def test___getitem___returns__contentitem(self,*args):
        "LineOrientedBuffer: buf[i] returns buf._content[i]"
        buf = LineOrientedBuffer()
        for buf._content in [ [],[''], ['\n',''],['text'],['ln 1\n','ln 2'] ]:
            for i in range(0,len(buf)):
                self.assertEqual(buf[i], buf._content[i])
                self.assertEqual(buf[:i], buf._content[:i])
                self.assertEqual(buf[i:], buf._content[i:])
        # TODO: test on real unicode strings? 
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: __setitem__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___setitem__(TestCase):
    def test___setitem___sets__contentitem(self,*args):
        "LineOrientedBuffer: buf[i] returns buf._content[i]"
        buf = LineOrientedBuffer()
        # TODO: write test
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: __iter__()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer___iter__(TestCase):
    def test___iter___returns__contentitem(self,*args):
        "LineOrientedBuffer: iter(buf) returns iter(buf._content)"
        buf = LineOrientedBuffer()
        for buf._content in [ [],[''], ['\n',''],['text'],['ln 1\n','ln 2'] ]:
            self.assertEqual(tuple(iter(buf)), tuple(iter(buf._content)))
        # FIXME: find a better way to verify identity?
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: _on_bind()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedTokenizer__on_bind(TestCase):
    def test__onbind_sets__doextend_default(self, *args):
        "LineOrientedBuffer: buf._on_bind(None) sets " \
        "buf._do_extend = buf._do_extend_default"
        buf = LineOrientedBuffer()
        self.assertIs(buf._on_bind(None), None)
        self.assertEqual(buf._do_extend, buf._do_extend_default)
    def test__onbind_sets__doextend_string(self, *args):
        "LineOrientedBuffer: buf._on_bind(\"foo\") sets " \
        "buf._do_extend = buf._do_extend_by_string"
        buf = LineOrientedBuffer()
        self.assertIs(buf._on_bind("foo"), "foo")
        self.assertEqual(buf._tell, 0)
        self.assertEqual(buf._do_extend, buf._do_extend_by_string)
    def test__onbind_sets__doextend_by_read(self, *args):
        "LineOrientedBuffer: buf._on_bind(readable) sets " \
        "buf._do_extend = buf._do_extend_by_read"
        class Readable(object):
            def read(self): pass
            def readline(self): pass
        buf = LineOrientedBuffer()
        readable = Readable()
        self.assertIs(buf._on_bind(readable), readable)
        self.assertEqual(buf._do_extend, buf._do_extend_by_read)
    def test__onbind_sets__doextend_by_iter(self, *args):
        "LineOrientedBuffer: buf._on_bind(iterable) sets " \
        "buf._do_extend = buf._do_extend_by_iter"
        class Iterable(object):
            def __iter__(self): return iter(['abc','def','ghi'])
        buf = LineOrientedBuffer()
        iterable = Iterable()
        rv = buf._on_bind(iterable)
        self.assertEqual(tuple(rv), tuple(iter(iterable)))
        self.assertEqual(buf._do_extend, buf._do_extend_by_iter)
#############################################################################
        
#############################################################################
# Test: LineOrientedBuffer: _do_assign()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer__do_assign(TestCase):

    def test__doassign_calls__makefsmstr_selectively(self, _make_fsm_str,*args):
        "LineOrientedBuffer: buf._do_assign(content) invokes " \
        "buf._make_fsm_str(buf, buf._content) when necessary"
        buf = LineOrientedBuffer()
        for content in [None, 'signle line', 'double\nline']:
            with patch.object(LineOrientedBuffer, '_make_fsm_str') as method:
                buf._do_assign(content)
                method.assert_called_once_with(buf._content)
        with patch.object(LineOrientedBuffer, '_make_fsm_str') as method:
            buf._do_assign('some\ncontent', fsm_str='b')
            self.assertFalse(method.called)

    @patch.object(LineOrientedBuffer, '_make_fsm_str')
    def test__doassign_accepts_string(self,*args):
        "LineOrientedBuffer: buf._do_assign(\"foo\\nbar\") sets " \
        "buf._content = [\"foo\\n\",\"bar\"]"
        buf = LineOrientedBuffer()
        for content in ['signle line', 'double\nline']:
            buf._do_assign(content)
            self.assertEqual(buf._content, content.splitlines())

    @patch.object(LineOrientedBuffer, '_make_fsm_str')
    def test__doassign_accepts_lists(self,*args):
        "LineOrientedBuffer: buf._do_assign(\"foo\") sets " \
        "buf._content = \"foo\""
        buf = LineOrientedBuffer()
        for content in [['signle line'], ['double\n','line']]:
            buf._do_assign(content)
            self.assertIs(buf._content,content)

    @patch.object(LineOrientedBuffer, '_make_fsm_str')
    def test__doassign_accepts_tuples(self,*args):
        "LineOrientedBuffer: buf._do_assign(\"foo\") sets " \
        "buf._content = \"foo\""
        buf = LineOrientedBuffer()
        for content in [('signle line',), ('double\n','line')]:
            buf._do_assign(content)
            self.assertEqual(buf._content, list(content))

    @patch.object(LineOrientedBuffer, '_make_fsm_str')
    def test__doassign_none2list(self,*args):
        "LineOrientedBuffer: buf._do_assign(None) sets buf._content = []"
        buf = LineOrientedBuffer()
        buf._do_assign(None)
        self.assertIsNot(buf._content,None)
        self.assertEqual(buf._content,[])
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: _do_extend_by_string()
#############################################################################
class Test_LineOrientedBuffer__do_extend_by_string(TestCase):
    @patch.object(LineOrientedBuffer,'_make_fsm_str')
    def test__doextendbystring_1(self,*args):
        "LineOrientedBuffer: buf._do_extend_by_string() works for some " \
        "simple test fixtures"
        _input = '012\n45678\n01'
        buf = LineOrientedBuffer()
        buf.bind(_input)
        self.assertEqual(buf._do_extend_by_string(3), 4) # full chunk
        self.assertEqual(''.join(buf[:]), _input[:4])
        self.assertEqual(buf._do_extend_by_string(6), 6) # full chunk
        self.assertEqual(''.join(buf[:]), _input[:10])
        self.assertEqual(buf._do_extend_by_string(6), 2) # tail
        self.assertEqual(''.join(buf[:]), _input[:])
#############################################################################

###############################################################################
### Test: LineOrientedBuffer: _do_extend_by_read()
###############################################################################
##class Test_LineOrientedBuffer__do_extend_by_read(TestCase):
##    def test__doextendbyread_1(self):
##        "LineOrientedBuffer: buf._do_extend_by_read() works for some " \
##        "simple test fixtures"
##        buf = LineOrientedBuffer()
##        # TODO: write this test
###############################################################################

#############################################################################
# Test: LineOrientedBuffer: _do_extend_by_iter()
#############################################################################
class Test_LineOrientedBuffer__do_extend_by_iter(TestCase):
    @patch.object(LineOrientedBuffer,'_make_fsm_str')
    def test__doextendbyiter_1(self,*args):
        "LineOrientedBuffer: buf._do_extend_by_iter() works for some " \
        "simple test fixtures"
        _input = [ '012\n', '45678\n' , '01' ]
        buf = LineOrientedBuffer()
        buf.bind(iter(_input))
        self.assertEqual(buf._do_extend_by_iter(3), 4) # '012'
        self.assertEqual(''.join(buf[:]), ''.join(_input)[:4])
        self.assertEqual(buf._do_extend_by_iter(6), 6) # full chunk
        self.assertEqual(''.join(buf[:]), ''.join(_input)[:10])
        self.assertEqual(buf._do_extend_by_iter(6), 2) # tail
        self.assertEqual(''.join(buf[:]), ''.join(_input)[:])
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: _update_end_marker()
#############################################################################
@patch.object(LineOrientedBuffer, '__init__', return_value = None)
class Test_LineOrientedBuffer__update_end_marker(TestCase):
    def setUp(self, *args):
        self._fixtures = [ { 
            # char:     0
            # col:      0
            'content': [],
            'markers' : [
                (0,  0,  0, 0,  0,  0),
                (1,  0,  0, 1,  0,  0),
                (0,  1,  0, 0,  1,  0),
                (0,  0,  1, 0,  0,  1),
            ]},
            {
            # char:     0
            # col:      0
            'content': [''],
            'markers' : [
                (0,  0,  0, 0,  0,  0),
                (1,  0,  0, 1,  0,  0),
                (0,  1,  0, 0,  1,  0),
                (0,  0,  1, 0,  0,  1),
            ]},
            {
            # char:      0123456789012345678
            # col:       0123456789012345678
            'content': ['single line content'],
            'markers' : [
                (0,  0,  0, 0, 19, 19),
                (1,  0,  0, 1, 19, 19),
                (0,  1,  0, 0, 20, 19),
                (0,  0,  1, 0, 19, 20),
            ]},
            {
            # char:       0   1234567890123456
            # col:        0   0123456789012345
            'content': ['\n','first line empty'],
            'markers' : [
                (0,  0,  0, 1, 16, 17),
                (1,  0,  0, 2, 16, 17),
                (0,  1,  0, 1, 16, 17),
                (0,  0,  1, 1, 16, 18),
            ]},
            {
            # char:      01234567890123456 7
            # col:       01234567890123456
            'content': ['second line empty\n',''],
            'markers' : [
                (0,  0,  0,  1,  0, 18),
                (1,  0,  0,  2,  0, 18),
                (0,  1,  0,  1,  0, 18),
                (0,  0,  1,  1,  0, 19),
            ]},
            {
            # char:      01234567 8   9012345
            # col:                    0123456
            'content': ['two line\n','content'],
            'markers' : [
                (0,  0,  0,  1,  7, 16),
                (1,  0,  0,  2,  7, 16),
                (0,  1,  0,  1,  7, 16),
                (0,  0,  1,  1,  7, 17),
            ]},
            {
            # char:      01234567 8   9012345 6
            # col:                    0123456 7
            'content': ['two line\n','content\n'],
            'markers' : [
                (0,  0,  0,  2,  0, 17),
                (1,  0,  0,  3,  0, 17),
                (0,  1,  0,  2,  0, 17),
                (0,  0,  1,  2,  0, 18),
            ]},
        ]

    @patch.object(LineOrientedBuffer,'_make_fsm_str')
    def test__updateendmarker_1(self, *args):
        "LineOrientedBuffer: buf._update_end_marker() works for several " \
        "test fixtures"
        buf = LineOrientedBuffer()
        for fix in self._fixtures:
            for markers in fix['markers']:
                buf._do_assign(fix['content'])
                buf._line_no, buf._col_no, buf._char_no = markers[:3]
                buf._end_line_no, buf._end_col_no, buf._end_char_no  \
                  = (buf._line_no, buf._col_no, buf._char_no)
                buf._update_end_marker()
                self.assertEqual(buf._end_line_no, markers[3])
                self.assertEqual(buf._end_col_no, markers[4])
                self.assertEqual(buf._end_char_no, markers[5])
#############################################################################

#############################################################################
# Test: LineOrientedBuffer: _make_fsm_str()
#############################################################################
class Test_LineOrientedTokenizer__make_fsm_str(TestCase):
    def test_makefsmstr_is_abstract(self):
        "LineOrientedBuffer._make_fsm_str is abstract" 
        with self.assertRaises(NotImplementedError): 
            LineOrientedBuffer._make_fsm_str('abc')
#############################################################################

if __name__ == "__main__":
    ldr = TestLoader()
    suite = unittest.TestSuite()
    # Load tests to test suite
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase___init__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_bind))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_set_start_marker))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_assign))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_extend))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_shift))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_bookmarking_accessors))
    suite.addTests(ldr.loadTestsFromTestCase(Test_TokenizerBufferBase_abstract_methods))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___init__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_bind))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_set_start_marker))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_assign))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_extend))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_shift))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer_bookmarking))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedTokenizer_fsm_str))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___str__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___unicode__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___len__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___getitem__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer___iter__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedTokenizer__on_bind))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer__do_assign))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer__do_extend_by_string))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer__do_extend_by_read))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer__do_extend_by_iter))
    suite.addTests(ldr.loadTestsFromTestCase(Test_CharOrientedBuffer__update_end_marker))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___init__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_bind))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_set_start_marker))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_assign))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_extend))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_shift))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer_bookmarking))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedTokenizer_fsm_str))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___str__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___unicode__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___len__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___getitem__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___setitem__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer___iter__))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedTokenizer__on_bind))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer__do_assign))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer__do_extend_by_string))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer__do_extend_by_iter))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedBuffer__update_end_marker))
    suite.addTests(ldr.loadTestsFromTestCase(Test_LineOrientedTokenizer__make_fsm_str))

    # TODO: load any other tests here

    unittest.TextTestRunner(verbosity = 2).run(suite)

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
