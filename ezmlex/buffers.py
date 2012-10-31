"""`ezmlex.buffers`

Input buffers for use with parsers/tokenizers.

The module provides buffer objects used by parsers/tokenizers implemented
elsewhere in `ezmlex` package. To start with buffers designed for
tokenizers read the documentation of `TokenizerBufferBase`.
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


class TokenizerBufferBase(object):
    """Base class for tokenizers' buffers.

    **General description**

    This is the base class for concrete input buffers used by `tokenizers`.
    A tokenizer input buffer reads input in chunks of predefined (custom) size
    and facilitates extraction of tokens of any length. A tokenizer buffer is
    a FIFO-like buffer, that internally holds a sequence of *"generalized
    characters"* (which we'll call the *items*) retrieved from some input
    source. Two basic operations on buffer are `extend()` to read chunk of data
    from input to the buffer and `shift()` to extract items from bufer.
    
    In ordinary case the *item* equals to single character and the
    buffer holds a string of characters (see `CharOrientedBuffer`).  However,
    we may also implement buffers for *items* other than characters, for
    exampe buffer with *items* being equal to physical lines of text kept
    internaly within a list (see `LineOrientedBuffer`).

    A tokenizer buffer provides following functions:

       - *input* binding, to read text from particular input, see `bind()`,
       - reading *items* from predefined input (attached with `bind()`) and
         appending them to the end of buffer, see `extend()`,
       - shifting out *items* from buffer, see `shift()`,
       - *bookmarking*, i.e. keeping up-to-date start and end text *markers*,
         which mark the start and end positions of buffer contents within
         input text. This information includes:

         - line number, see `line_no()` and `end_line_no()`,
         - column number within the line, see `col_no()` and `end_col_no()`,
         - character offset relative to the beginning of input, see
           `char_no()` and `end_char_no()`.

       - returning "cannonical" representation of buffer's content, which we
         call here *FSM string*, see `fsm_str()`,
       - returning string representation of buffer contents, see `__str__()`
         and `__unicode__()`.
       - accessing buffer items via `__getitem__()`,
       - iterator interface, see `__iter__()`

    The start marker tells where in the input text is located the beginning of
    the content currently held in the buffer. The end marker points to a
    character in the input text (or after the text), that would start an
    item being one past the last item currently hold in buffer (e.g.  first
    character of the line following last buffered line in
    `LineOrientedBuffer`).  The start marker may be set at any time to custom
    position with `set_start_marker()`.  The end marker is updated internally
    each time the start marker is altered (e.g.  `set_start_marker()`,
    `assign()`) or the buffer content changes (e.g.  `extend()`, `shift()`). 

    Note:
       The buffer content and *bookmarking* state will usually change when
       `extend`'ing, `shift`'ing and `assign`'ing, but they are totally
       independent of input `bind`'ing.  Buffer content and *bookmarking*
       state remain unaltered when `bind`'ing to (another) input. One may,
       for example, bind file IO object as input, read it, then bind another
       IO object, and the result shall be the same as the result of reading
       concatenated contents of the files as a whole (markers keep moving
       without discontinuities). 

    **FSM string**

    A tokenizer buffer may be requested to return so called *FSM string*
    (Finite State Machine string), which is a kind of canonical representation
    of buffer's content.  Tokenizers match buffer's *FSM string* against
    regular expressions to recognize tokens in that buffer. In simplest case
    the *FSM string* may be equivalent to the string held in the buffer. In
    general, however, it is only assumed that consecutive characters in *FSM
    string* correspond to *items* in the buffer. Conversion from *items* to
    *FSM string* may, in general, depend on lexical grammar used by given
    tokenizer. In that case the conversion shall be delegated to that tokenizer
    (see `_make_fsm_str()`). Even if the conversion is delegated, the buffer
    still drives the update of its *FSM string*. The update may extend the *FSM
    string* when `extend()` is called or shift its characters when `shift()` is
    called. This allows to keep *FSM string* in sync with the internally
    managed sequence of *items*.

    **Making use of TokenizerBufferBase**

    To use `TokenizerBufferBase` class you should create a subclass of it and
    the subclass must provide implementation of the following methods:

        - `fsm_str()`,
        - `__str__()`, `__unicode__()`,
        - `__len__()`, `__getitem__()`,
        - `__iter__()`,
        - `_do_assign()`, `_do_extend()`,
        - `_update_end_marker()`,
        - `_make_fsm_str()`.

    Usually, it is also necessary to re-implement the method:

        - `_on_bind()`,

    in order to perform custom operations at the time a new input is bound
    to a buffer being implemented.

    In most cases it's not necessary to derive directly from
    `TokenizerBufferBase`, as one may use `CharOrientedBuffer` or
    `LineOrientedBuffer` depending on needs. For these classes, the subclass
    have to implement just the `_make_fsm_str()`.
    """

    _default_chunk = 32
    """Default chunk size for the buffer.

    This is the default number of characters being read from input with
    single call to `extend()`. It is used, when the `extend()` is invoked
    without ``chunk_size`` parameter. Note, that this value is not strictly
    respected, and actual number of characters retrieved might vary (e.g. in
    `LineOrientedBuffer`). For more details see documentation of `extend()`.
    """

    def __init__(self, _input = None, line_no = 0, col_no = 0, char_no = 0,
                 content = None, **kw):
        """Initializes buffer object.

        The ``_input`` is attached to buffer with `bind()`. The ``line_no``,
        ``col_no``, ``char_no`` and ``content`` parameters have same effect as
        in `assign()`. 

        :Parameters:
            _input
                input used to read items from,
            line_no
                line number used to initialize the start marker; line numbers
                are zero-based,
            col_no
                column index within current line, used to initialize the start
                marker; column indices are zero based,
            char_no
                character offset used to initialize the start marker,
            content
                optional content to initialize buffer with.
        
        :Keywords:
            kw
                optional keywords passed to `assign()`.

        """
        self.bind(_input)
        self.assign(line_no, col_no, char_no, content, **kw)

    #
    # Buffer setup
    #
    def bind(self, _input):
        """Bind input to this buffer object.
        
        After successful bind, subsequent calls to `extend()` read data from
        the ``_input`` until end of input is reached. If input is `None`,
        then the current input is detached.

        Valid input types are different for different subclasses of
        `TokenizerBufferBase` and are defined by the subclasses.

        :Parameters:
            _input
                input object that will be used to read items from; valid input
                types are different for different subclasses of
                `TokenizerBufferBase` and are defined by the subclasses.
        """
        self._input = self._on_bind(_input)

    def set_start_marker(self, line_no, col_no, char_no):
        """Move the start marker to custom position.

        After start marker is changed, the end marker is updated by call to 
        `_update_end_marker()`.

        :Parameters:

            line_no
                line number of new starting position; line numbers are
                zero-based,
            col_no
                column index within current line, of the new starting
                position; column indices are zero based,
            char_no
                character offset of new starting position.
        """
        self._line_no = line_no
        self._col_no = col_no
        self._char_no = char_no
        self._update_end_marker()

    #
    # Buffer content management
    #
    def assign(self, line_no, col_no, char_no, content, **kw):
        """Assign new content and start marker position to the buffer.

        First, the new `content` is assigned to the buffer, then start
        marker is moved to the position defined by (``line_no``, ``col_no``,
        ``char_no``) exactly as it is done by `set_start_marker()` which also
        updates the end marker.

        :Parameters:
            line_no
                line number of new starting position; line numbers are
                zero-based,
            col_no
                column index within current line, of the new starting
                position; column indices are zero based,
            char_no
                character offset of new starting position,
            content
                new content to assign, or ``None`` (to clear content),
        :Keywords:
            kw
                keyword parameters passed to `_do_assign()`; following
                keywords may be passed by other methods of
                `TokenizerBufferBase`:
                
                - ``fsm_str``: supplies initial *FSM string*; this is passed
                  by `shift()` method
        """
        self._do_assign(content,**kw)
        self.set_start_marker(line_no, col_no, char_no)

    def extend(self, chunk_size = None):
        """Read *items* from input and append them to the buffer.

        This method tries to append new *items* to buffer by reading ``n >=
        chunk_size`` characters from the input (see `bind()`). Note, that
        `chunk_size` is not guaranted to be strictly respected. If there is not
        enought text in the input, the method is not able to read `chunk_size`
        characters. In this case, the method reads only available amount of
        data. Moreover, for buffers, for which *items* are not equivalent with
        characters, it may be impossible to retrieve a number of complete items
        by reading exactly `chunk_size` characters. This is for example the
        case of `LineOrientedBuffer`, which keeps lines of text as items. In
        such case additional characters may be read from input to fully recover
        otherwise incomplete item. 
        
        If ``chunk_size`` is ``None`` or is not provided, the default value
        defined by class attribute `_default_chunk` is used.  The default
        value, `_default_chunk`, may be redefined in subclasses.  

        :Parameters:
            chunk_size
                (not strict) number of characters to retrieve from input,

        :Return:
            number of items appended to the buffer.
        """
        if chunk_size is None:
            chunk_size = self._default_chunk
        size = self._do_extend(chunk_size)
        self._update_end_marker()
        return size

    def shift(self, count = None):
        """Shift out `count` items from the buffer

        The method shifts out first `count` items from the buffer and updates
        its *bookmarking* state accordingly (start marker). The shifted out
        items are returned as a new buffer object.

        :Parameters:
            count
                number of items to be shifted out from the buffer, it must
                satisfy condition ``0 <= count < len(self)``.

        :Return:
            new buffer of same type containing shifted out *items*.
        """
        if count is None:
            count = len(self)
        # Return shifted-out items encapsulated within a new instance of
        # buffer.
        s = self.__class__( None, self.line_no(), self.col_no(),
                                     self.char_no(), self[:count],
                                     fsm_str = self.fsm_str()[:count] )
        # Modify starting position and assign new content
        self.assign(s.end_line_no(), s.end_col_no(), s.end_char_no(),
                    self[count:], fsm_str = self.fsm_str()[count:])
        return s

    #
    # Querying buffer state
    #
    def line_no(self):
        """Return line position of the start marker.
        
        Return line number within original (input) text, at which the
        beginning of buffer's content is located. The position of the
        beginning of buffer's content within original text is called here a
        start marker. The function returns line number of the line at which
        the start marker is located.
        
        Line numbering is zero-based, so for the first line of input it holds
        ``line_no()==0``."""
        return self._line_no

    def col_no(self):
        """Return column offset of the start marker.

        Return column offset within a line of original (input) text, at which 
        the begining of the buffer's content is located. The position of the
        beginning of buffer's content within the original (input) text is
        called here a start marker. The function returns the column number
        (character within line) at which the start marker is located."""
        return self._col_no

    def char_no(self):
        """Return character offset of the start marker.
        
        Return character offset of the beginning of first item in buffer
        within original (input) text.  The position of the beginning of the
        of buffer's content within the original (input) text is called here
        a start marker. The function returns the character offset relative to
        the beginning of input text of the character at which the start
        marker is located."""
        return self._char_no

    def end_line_no(self):
        """Return line position of the end marker.
       
        The end marker is the position within input text at which the 
        one past last item would start. This function returns line number
        of the line at which the end marker is located.
        """
        return self._end_line_no

    def end_col_no(self):
        """Return column offset of the end marker.
       
        The end marker is the position within input text at which the 
        one past last item would start. This function returns column number
        of the column at which the end marker is located.
        """
        return self._end_col_no

    def end_char_no(self):
        """Return character offset of the end marker.
       
        The end marker is the position within input text at which the 
        one past last item would start. This function returns character offset
        measured from the beginning of input stream of the character at which
        the end marker is located.
        """
        return self._end_char_no

    def fsm_str(self):
        """Return the *FSM string* representation of buffer content.

        This is an abstract method and must be implemented in a subclass.

        For details see *FSM string* section of `TokenizerBufferBase`
        documentation.

        :Return:
            *FSM string*
        """
        raise NotImplementedError("this method is abstract")

    #
    # Methods to overwrite in subclasses
    #
    def __str__(self):
        """Return the string representation of buffer's content.

        The method is designated to recover the part of original text 
        (provided by input) that is currently stored in the buffer.

        The method is abstract and must be implemented in a subclass.
        """
        raise NotImplementedError("this method is abstract")

    def __unicode__(self):
        """Return the string representation of buffer's content.

        This is unicode version of `__str__()`.

        The method is abstract and must be implemented in a subclass.
        """
        raise NotImplementedError("this method is abstract")

    def __len__(self):
        """Return length of the buffer measured in number of items held.

        The method is abstract and must be implemented in a subclass.
        """
        raise NotImplementedError("this method is abstract")

    def __getitem__(self, index):
        """Get item(s) value(s) from buffer.

        The method is abstract and must be implemented in a subclass.

        *Example notations:*

        .. python::

            buffer[1]
            buffer[1:10]
            buffer[:10]
        
        :Parameters:
            index
                index of item to access, or a slice.
        :Returns:
            requested items
        """
        raise NotImplementedError("this method is abstract")

    def __iter__(self):
        """Iterator interface, used to iterate through buffers *items*.

        The method is abstract and must be implemented in a subclass.
       
        *Example*:

        .. python::

            for item in iter(buffer):
                # do something with item
        """
        raise NotImplementedError("this method is abstract")

    def _on_bind(self, _input):
        """Method called just before the `_input` is bound to the buffer.
        
        This method should be implemented in a subclass. Here the buffer object
        should be preconfigured to read from ``_input`` (e.g. read method may
        be selected accordingly to the type of ``_input``). The defatult
        implementation just returns ``_input``.

        :Parameters:
            _input
                input object provided by user.
        :Return:
            should return `_input` or appropriate object representing input,
            that will be used by buffer to read input. The returned object
            is assigned to ``self._input`` attribute.
        """
        return _input

    def _do_assign(self, content, **kw):
        """Method called by `assign()` to setup buffer's content.

        This method must be implemented in a subclass. Its responsibility
        is to replace old buffer's content with new content provided through
        `content` parameter. 

        Note:
            The implementation of `_do_assign()` should not alter
            *bookmarking* state. The bookmarking state is updated
            automatically by `assign()`. 

        Note:
            The implementation of `_do_assign()` must handle special
            case when ``content`` is ``None`` and set-up its internal object
            storing the content to its specific ``empty`` state. Typical
            example is for a buffer which stores data as string:

            .. python::

                def _do_assign(self, content, **kw):
                    if content is None:
                        self._content = ''
                    else:
                        self._content = content

        :Parameters:
            content
                new content to assign, or ``None``.
        :Keywords:
            kw
                additional keyword parameters provided by user to `assign()`.
        :Return:
            nothing
        """
        raise NotImplementedError("this method is abstract")

    def _do_extend(self, chunk_size):
        """Method called by `extend()` to read items into buffer.

        This method must be implemented in a subclass. Its responsibility
        is to retrieve appropriate number of *items* from input and append
        them to the buffers content.

        Note:
            The implementation of `_do_extend()` should not alter
            *bookmarking* state. The bookmarking state is updated
            automatically by `extend()`. 

        :Parameters:
            chunk_size
                same as for `extend()`.
        :Return:
            number of items appended to the buffer.
        """
        raise NotImplementedError("this method is abstract")

    def _update_end_marker(self):
        """Reposition end marker.
        
        This method must be implemented in a subclass. It shall update the 
        values of ``self._end_line_no``, ``self._end_col_no`` and
        ``self._end_char_no`` that define current position of end marker.
        The procedure must take into account the current position of start
        marker and the content of the buffer.

        :Returns:
            nothing
        """
        raise NotImplementedError("this method is abstract")

    @classmethod
    def _make_fsm_str(cls, items):
        """Convert items to *FSM string*
        
        This method may be implemented by a subclass. It is only necessary 
        when the *FSM string* is not equivalent to the buffer content. 
        Otherwise `fsm_str()` may return directly the string held in buffer.
        """
        raise NotImplementedError("this method is abstract")


class CharOrientedBuffer(TokenizerBufferBase):
    """Tokenizer buffer which holds bare characters. 

    **General description**

    The `CharOrientedBuffer` object buffers original characters retrieved from
    its input. The characters are keept in an internal string object.

    **Supported input types**

    Supported input types (``_input`` parameter to `bind()` and `__init__()`)
    are:

        - strings, i.e. ``str``, and ``unicode`` objects,
        - IO objects, having ``read()`` method (e.g. `file object`_)
        - objects that provide iterator interface for iterating 
          through parts of text (usually lines).

    The following snippets show how one may attach different inputs to a buffer.

    **Example**: using text file (ASCII) as input

    .. python::

        from ezmlex.buffers import CharOrientedBuffer
        class Buffer(CharOrientedBuffer):
            @classmethod
            def _make_fsm_str(cls, items):
                return items
        buf = Buffer(open('file.txt','rU'))
        ...

    **Example**: using text file (UTF-8) as input

    .. python::

        from ezmlex.buffers import CharOrientedBuffer
        import codecs
        class Buffer(CharOrientedBuffer):
            @classmethod
            def _make_fsm_str(cls, items):
                return items
        buf = Buffer(codecs.open('file.txt','rU','utf-8'))
        ...

    **Example**: using list with text lines as input (iterator interface)

    .. python::

        from ezmlex.buffers import CharOrientedBuffer
        class Buffer(CharOrientedBuffer):
            @classmethod
            def _make_fsm_str(cls, items):
                return items
        input = [ u'first line\\n', u'second line\\n' ]
        buf = Buffer(input)
        ...

    **Making use of CharOrientedBuffer**
    
    To make use of the `CharOrientedBuffer` one has do derive its own buffer
    subclass which implements the `_make_fsm_str()` class method. The following
    examples show simple usage cases to get an idea how the buffer works.

    **Example**: read chunks of 32 characters and output chunks of 
    8 characters

    .. python::

        from ezmlex.buffers import CharOrientedBuffer
        class Buffer(CharOrientedBuffer):
            @classmethod
            def _make_fsm_str(cls,items):
                return items
        txt = \"\"\"Lorem ipsum dolor sit amet, consectetur adipiscing
        elit. Sed aliquet odio quis elit aliquet eu interdum justo
        adipiscing. Vestibulum sodales ornare adipiscing.\"\"\"
        buf = Buffer(txt)
        while buf.extend(32):
            while 8 <= len(buf):
                s = buf.shift(8)
                print "%d:%d:%r" % (s.line_no(), s.col_no(), s.__str__())
        if len(buf):
            # Print out remaining part of text (a tail shorter than 8 chars)
            print "%d:%d:%r" % (buf.line_no(), buf.col_no(), buf.__str__())

    The output generated by above script shall be::

        0:0:'Lorem ip'
        0:8:'sum dolo'
        0:16:'r sit am'
        0:24:'et, cons'
        0:32:'ectetur '
        0:40:'adipisci'
        0:48:'ng\\nelit.'
        1:5:' Sed ali'
        1:13:'quet odi'
        1:21:'o quis e'
        1:29:'lit aliq'
        1:37:'uet eu i'
        1:45:'nterdum '
        1:53:'justo\\nad'
        2:2:'ipiscing'
        2:10:'. Vestib'
        2:18:'ulum sod'
        2:26:'ales orn'
        2:34:'are adip'
        2:42:'iscing.'

    The above example may be found in
    ``examples/apidoc/CharOrientedBuffer1.py``.

    **Example**: read words from input, treat all other tokens as errors

    .. python::

        import re
        from ezmlex.buffers import CharOrientedBuffer
        class Buffer(CharOrientedBuffer):
            @classmethod
            def _make_fsm_str(cls,items):
                return items
        txt = \"\"\"Lorem ipsum dolor sit amet, consectetur adipiscing
        elit. Sed aliquet odio quis elit aliquet eu interdum justo
        adipiscing. Vestibulum sodales ornare adipiscing.\"\"\"
        buf = Buffer(txt)
        word = re.compile(r'[a-zA-Z]+')
        sep = re.compile(r'[ \\t\\n]+')
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

    The output from above script shall be::

        0:0:word:'Lorem'
        0:6:word:'ipsum'
        0:12:word:'dolor'
        0:18:word:'sit'
        0:22:word:'amet'
        0:26:error:','
        0:28:word:'consectetur'
        0:40:word:'adipiscing'
        1:0:word:'elit'
        1:4:error:'.'
        1:6:word:'Sed'
        1:10:word:'aliquet'
        1:18:word:'odio'
        1:23:word:'quis'
        1:28:word:'elit'
        1:33:word:'aliquet'
        1:41:word:'eu'
        1:44:word:'interdum'
        1:53:word:'justo'
        2:0:word:'adipiscing'
        2:10:error:'.'
        2:12:word:'Vestibulum'
        2:23:word:'sodales'
        2:31:word:'ornare'
        2:38:word:'adipiscing'
        2:48:error:'.'

    The above example may be found in
    ``examples/apidoc/CharOrientedBuffer2.py``.

    .. _`file object` : http://docs.python.org/library/stdtypes.html#file-objects 
    """
    
    _default_chunk = 32
    """Default chunk size for `extend()` measured in characters."""

    def __init__(self, *args, **kw): 
        TokenizerBufferBase.__init__(self, *args, **kw)

    def fsm_str(self):
        """Return *FSM string* representation of buffer content.

        For definition of *FSM string* see docs for `TokenizerBufferBase`."""
        return self._fsm_str

    def _on_bind(self, _input):
        from ezmlex.util import is_string
        if _input is None:
            self._do_extend = self._do_extend_default
            return _input
        # If string given as input, we'll walk through it using our own seek 
        # pointer.
        if is_string(_input):
            self._tell = 0
            self._do_extend = self._do_extend_by_string
            return _input
        # If it's something that have 'read()' method, we'll read characters in
        # chunks.
        try:
            read = _input.read
            if callable(read):
                self._do_extend = self._do_extend_by_read
                return _input
        except AttributeError: pass
        # Otherwise we'll try to read input's native portions using iterator
        # interface
        _input = iter(_input)
        self._do_extend = self._do_extend_by_iter
        return _input
        
    def _update_end_marker(self):
        nchars = len(self._content)
        nlines = self._content.count('\n')
        self._end_char_no = self.char_no() + nchars
        self._end_line_no = self.line_no() + nlines
        if nlines == 0:
            self._end_col_no = self.col_no() + nchars
        else:
            self._end_col_no = nchars - (self._content.rfind('\n') + 1)
        
    def __str__(self):
        return self._content

    def __unicode__(self):
        return self._content

    def __len__(self):
        return len(self._content)

    def __getitem__(self, index):
        return self._content[index]

    def __iter__(self):
        return iter(self._content)

    def _do_assign(self, content, **kw):
        if content is None:
            self._content = ''
            self._fsm_str = ''
        else:
            self._content = content
            self._fsm_str = self._make_fsm_str(content)

    def _do_extend_by_string(self, chunk_size):
        beg = self._tell
        end = min(self._tell + chunk_size, len(self._input))
        if end > self._tell:
            self._content += self._input[beg:end]
            self._fsm_str += self._make_fsm_str(self._input[beg:end])
            self._tell = end
        return (end - beg)

    def _do_extend_by_read(self, chunk_size):
        string = self._input.read(chunk_size)
        self._content += string
        self._fsm_str += self._make_fsm_str(string)
        return len(string)

    def _do_extend_by_iter(self, chunk_size):
        size = 0
        try:
            while size < chunk_size:
                part = self._input.next()
                size += len(part)
                self._content += part
                self._fsm_str += self._make_fsm_str(part)
        except StopIteration:
            pass
        return size

    def _do_extend_default(self, chunk_size):
        raise RuntimeError('input method unspecified. Input: %r' % self._input)

    _do_extend = _do_extend_default

# NOTE: The internal list for two distinct cases
#   []      no lines (empty buffer)
#   ['']    single empty line in buffer
# The empty buffer must not alter output text when used in concatenation and so
# on.
class LineOrientedBuffer(TokenizerBufferBase):
    """Tokenizer buffer which holds lines of text as items. 

    **General description**

    This object buffers lines of text retrieved from input. The lines are
    keept in an internal list object. The `TokenizerBufferBase` object also
    maintains its *FSM string* (see `TokenizerBufferBase` for definition of
    *FSM string*). Characters in the *FSM string*  represent consecutive lines
    from the buffer, i.e.  ``n``-th character in the *FSM string* corresponds
    to ``n``-th line in buffer (the first line in the buffer has ``n = 0``).  

    **Complete and incomplete lines**

    Items held in buffer are strings ended with ``\\n`` character (*complete
    lines*). Only the last item may be a string without ``\\n`` in which case
    it is interpreted as *incomplete line*. If the buffer ends with incomplete
    line, the next call to `extend()` will append the first line retrieved
    from input to that incomplete line (no new item is created in the buffer
    for that line). If the buffer ends with complete line, the first line read
    from input will be appended to the buffer as new item.
    
        
    Let there be a `LineOrientedBuffer` object ``buf`` which already has
    following items (all lines are complete):

    .. python::

        >>> buf[:]
        ['first line\\n', 'second line\\n'].
    
    Then the following code

    .. python::
        
        >>> _input = ['input line\\n'].
        >>> buf.bind(_input)
        >>> buf.extend()  
        11

    appends new line item to the buffer, after which the buffer has items:

    .. python::

        >>> buf[:]
        ['first line\\n', 'second line\\n', 'input line\\n']

    Now assume, that the buffer ends with incomplete line, for example its
    content is

    .. python::
        >>> buf[:]
        ['first line\\n', 'second line']
    
    By executing the same code with the same ``_input`` 
    
    .. python::

        >>> _input = ['input line\\n'].
        >>> buf.bind(_input)
        >>> buf.extend()
        11

    we obtain 

    .. python::

        >>> buf[:]
        ['first line\\n', 'second lineinput line\\n']

    **Incomplete lines and __len__()**

    The `LineOrientedBuffer.__len__()` returns the number of all items in
    buffer, including the *incomplete line* (if present). This may be
    illustrated by the following example:

    .. python::
        
        >>> buf[:]
        ['first line\\n', 'second line\\n', 'incomplete line']
        >>> len(buf) # returns 3
        3

    **Making use of LineOrientedBuffer**

    To use `LineOrientedBuffer` class, you should create a subclass which
    provides implementation of `_make_fsm_str()`. The method should accept a
    list of strings (lines) and return corresponding *FSM string*. The
    operation is usually delegated to a tokenizer class which wants to use the
    buffer subclass. The method receives list of all items that have to be 
    processed.

    **Supported input types**

    Supported input types (``_input`` parameter to `bind()` and `__init__()`)
    are:

        - strings, i.e. ``str``, and ``unicode`` objects,
        - objects, having both ``read()`` and ``readline()`` methods identical
          to these defined by `file object`_,
        - objects that provide iterator interface (``__iter__``); iterator
          should iterate through pieces of string, usually lines; the items
          returned by iterator must include all endline characters which are
          present in original input text.

    **Example**: recognize comments (lines starting with ``#``), plain lines
    and detect incomplete line

    .. python::

        import re
        from ezmlex.buffers import LineOrientedBuffer
        class MyBuffer(LineOrientedBuffer):
            #
            _re_comment = re.compile(r'#.*\\n')
            _re_line = re.compile(r'(?:[^#].*)?\\n')
            #
            @classmethod
            def _make_fsm_str(cls, items):
                def _fsm_char(item):
                    if cls._re_comment.match(item): return '#'
                    elif cls._re_line.match(item):  return 'L'
                    else:                           return 'I'
                #
                return ''.join(map(_fsm_char, items))

        txt = \"\"\"Lorem ipsum dolor sit amet,
        consectetur adipiscing elit. 

        # Sed aliquet odio quis elit aliquet 
        # eu interdum justo adipiscing.

        Nullam sollicitudin cursus neque, id 
        semper diam viverra ac.

        # In mattis tempus condimentum.\"\"\"

        buf = MyBuffer(txt)
        buf.extend()
        while len(buf):
            fsm_str = buf.fsm_str()
            if fsm_str[0] == '#':   id = 'comment:   '
            elif fsm_str[0] == 'L': id = 'line:      '
            else:                   id = 'incomplete:'
            s = buf.shift(1)
            print "%d:%d:%s%r" % (s.line_no(), s.col_no(), id, s.__str__())
            if len(buf) == 0:
                buf.extend() 
        
    The output from above script shall be::

        0:0:line:      'Lorem ipsum dolor sit amet,\\n'
        1:0:line:      'consectetur adipiscing elit. \\n'
        2:0:line:      '\\n'
        3:0:comment:   '# Sed aliquet odio quis elit aliquet \\n'
        4:0:comment:   '# eu interdum justo adipiscing.\\n'
        5:0:line:      '\\n'
        6:0:line:      'Nullam sollicitudin cursus neque, id \\n'
        7:0:line:      'semper diam viverra ac.\\n'
        8:0:line:      '\\n'
        9:0:incomplete:'# In mattis tempus condimentum.'

    .. _`file object` : http://docs.python.org/library/stdtypes.html#file-objects 
    """

    _default_chunk = 256
    """Default chunk size for `extend()` measured in characters."""

    def __init__(self, *args, **kw):
        TokenizerBufferBase.__init__(self, *args, **kw)

    def _on_bind(self, _input):
        from ezmlex.util import is_string
        if _input is None:
            self._do_extend = self._do_extend_default
            return _input

        # If string given as input, we'll walk through it using our own seek 
        # pointer.
        if is_string(_input):
            self._tell = 0
            self._do_extend = self._do_extend_by_string
            return _input

        # If it's something that have 'read()' and 'readline()' methods, we'll
        # read characters in chunks.
        try:
            if callable(_input.read) and callable(_input.readline):
                self._do_extend = self._do_extend_by_read
                return _input
        except AttributeError: 
            pass

        # Otherwise we'll try to read input's native portions using iterator
        # interface
        _input = iter(_input)
        self._do_extend = self._do_extend_by_iter
        return _input

    def fsm_str(self):
        """Return *FSM string* representation of buffer content.

        For definition of *FSM string* see documentation of
        `TokenizerBufferBase`.

        This implementation returns *FSM string* computed by `_make_fsm_str`.
        """
        return self._fsm_str

    def __str__(self):
        return ''.join(self._content)

    def __unicode__(self):
        return ''.join(self._content)

    def __len__(self):
        """Returns number of lines in buffer, including the *incomplete line*
        (see docs for `LineOrientedBuffer`) if present"""
        return len(self._content)

    def __getitem__(self, index):
        return self._content[index]

    def __setitem__(self, index, content):
        self._content[index] = content 
        self._fsm_str[index] = self._make_fsm_str(content)

    def __iter__(self):
        return iter(self._content)

    def _update_end_marker(self):
        nlcnt = len(self._content)
        if nlcnt and (not self._content[-1].endswith('\n')):
            nlcnt -= 1
            if(nlcnt == 0):
                # Our content consists of one incomplete line
                self._end_col_no = self._col_no + len(self._content[-1])
            else:
                # We have more than one line and the last one is incomplete
                self._end_col_no = len(self._content[-1])
        else:
            if(nlcnt == 0):
                # We have empty buffer
                self._end_col_no = self._col_no
            else:
                # We have buffer with all lines complete
                self._end_col_no = 0
        chcnt = sum(map(lambda x : len(x), self._content))
        self._end_line_no = self.line_no() + nlcnt
        self._end_char_no = self.char_no() + chcnt

    def _do_assign(self, content, **kw):
        from ezmlex.util import is_string, is_list
        if content is None:
            self._content = []
            self._fsm_str = self._make_fsm_str([])
            return
        if is_string(content):
            self._content = content.splitlines()
        elif not is_list(content):
            self._content = list(content)
        else:
            self._content = content
        if 'fsm_str' in kw:
            self._fsm_str = kw['fsm_str']
        else:
            self._fsm_str = self._make_fsm_str(self._content)
            
    def _do_append_line(self, line):
        if self._content and (not self._content[-1].endswith('\n')):
            # concatenate to last line in buffer (the last line
            # is not complete)
            self._content[-1] += line
            self._fsm_str = self._fsm_str[:-1] \
                          + self._make_fsm_str(self._content[-1:])
        else:
            self._content.append(line)
            self._fsm_str += self._make_fsm_str([line])

    def _do_append_string_lines(self, string):
        if not string: return
        lines = string.splitlines(True)
        if self._content and (not self._content[-1].endswith('\n')):
            self._content[-1] += lines[0]
            self._fsm_str = self._fsm_str[:-1] \
                          + self._make_fsm_str(self._content[-1:])
            self._content.extend(lines[1:])
            self._fsm_str += self._make_fsm_str(lines[1:])
        else:
            self._content.extend(lines)
            self._fsm_str += self._make_fsm_str(lines)

    def _do_extend_by_string(self, chunk_size):
        # TODO: test it
        input_len = len(self._input)
        end = min(input_len, self._tell + chunk_size)
        if self._tell < end:
            if not (self._input[end-1] == '\n'):
                try:
                    end = self._input.index('\n', end-1) + 1
                except ValueError:
                    end = input_len
            self._do_append_string_lines(self._input[self._tell : end])
            size = end - self._tell
            self._tell = end
        else:
            size = 0
        return size 

    def _do_extend_by_read(self, chunk_size):
        # TODO: test it
        chunk = self._input.read(chunk_size)
        if chunk:
            self._do_append_string_lines(chunk)
            size = len(chunk)
            if not (chunk[-1] == '\n'):
                tail = self._input.readline()
                self._do_append_string_lines(tail)
                size += len(tail)
        else:
            size = 0
        return size

    def _do_extend_by_iter(self, chunk_size):
        # TODO: test it
        size = 0
        try:
            while size < chunk_size:
                line = self._input.next()
                if not line:
                    break # end of input
                self._do_append_line(line)
                size += len(line)
        except StopIteration:
            pass
        return size

    def _do_extend_default(self, chunk_size):
        raise RuntimeError('input method unspecified. Input: %r' % self._input)

    _do_extend = _do_extend_default

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
