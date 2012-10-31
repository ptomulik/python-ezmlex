"""`ezmlex.tokenizers`

Please start with the documentation of `TokenizerBase` class.
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
from ezmlex.patterns import ccat, ccatg
from ezmlex.tokens import TokenBase
from ezmlex.buffers import LineOrientedBuffer


class TokenizerBase(object):
    """Base class for regexp-based tokenizers.

    A tokenizer is an object which recognizes tokens in text. Tokens may be
    read one at a time via `token()` method or iterator interface. The term
    ``token`` is somehow general here.  With this library you can, for
    example, construct "traditional" tokenizers for which tokens are entities
    (words, numers, ..) composed from single characters, but it is also easy
    to create a non-usual tokenizer which defines tokens to be multiline
    comments or text paragraphs composed from lines of text (text line plays
    same role as single character in traditional tokenizers).
    
    I use an intermediate representation of input string which I call an FSM
    string (Finite State Machine string). Before recognizing tokens, the FSM
    representation of input string is determined (for ordinary cases the FSM
    string equals to input string). The FSM string is then matched against
    regular expressions to recognize tokens within the text. For example,
    line-oriented tokenizers will map each input line to a single FSM character
    and form FSM string from these FSM characters. The multiline paragraph will
    yield multi-character word in FSM string. Certain types of paragraphs will
    be then recognized by recognizing certain words in FSM string.

    **Making use of TokenizerBase** 

    The intended use of `TokenizerBase` is to first derive new tokenizer class,
    define its lexical grammar and then create an instance of new tokenizer
    object to process text streams.

    A gramar for new tokenizer class is defined by definig token types and
    error token types. The grammar also includes the definition of mapping
    from input texts to FSM strings.

    **Tokenizer's buffer**

    Each instance of tokenizer must have attached a buffer object (an instance
    of `TokenizerBufferBase`). The reference to buffer object should be stored
    in ``_buffer`` attribute of the tokenizer. The buffer stores a piece of
    text that has already been read from input stream but has not been
    converted to tokens yet. The buffer also keeps "bookmarking" information
    determining the position of buffered content in the original stream (line
    index, column index, character offset).  For more details about buffers see
    documentation of the `ezmlex.buffers` module.

    A new ``Tokenizer`` class derived from `TokenizerBase` must implement
    `_init_buffer()` method which instantiates the buffer and stores its
    reference in ``_buffer`` attribute. An example is given below.

    **Example** Implementing `_init_buffer()` method

    .. python::

        from ezmlex.tokenizers import TokenizerBase
        # Assuming that Buffer class is defined somewhere ...
        class Tokenizer(TokenizerBase):
            def _init_buffer(self, *args, **kw):
                self._buffer = Buffer(*args,**kw)

    **FSM character patterns**

    One step in lexical grammar definition is to define transformation from
    input text to FSM string. The transformation is performed by 
    ``Buffer._make_fsm_str()`` and is often delegated to a tokenizer.

    `TokenizerBase` facilitaties mapping pieces of input text into FSM
    characters by using FSM character patterns. This is used, for example,
    by tokenizers that map entire lines into FSM characters. First, some
    patterns must be defined. The patterns are then used to classify each item
    from buffer and return corresponding FSM character. In `LineOrientedBuffer`,
    for example, one may replace each comment line with ``#``, each empty line
    with space and each non-empty and non-comment line with a letter. 

    FSM character patterns must carefully designed such that any possible input
    item matches at most one FSM character pattern. The null character
    ``\\0`` in FSM string has special meaning. Each unrecognized item from
    input buffer (i.e. an item that doesn't match any of FSM char patterns)
    should be mapped to ``\\0`` in FSM string.

    FSM character pattern may be defined with `def_fsm_char_pattern()`. 
    A previously registered character pattern may be retrieved with
    `fsm_char_pattern()`. The dictionary of all registered FSM character
    patterns may be retrieved with `fsm_char_patterns()`. Pattern may be
    removed from the dictionary with `del_fsm_char_pattern()`.

    **Example** defining FSM character patterns

    .. python::

        from ezmlex.tokenizers import TokenizerBase

        class Tokenizer(TokenizerBase):
            ...

        Tokenizer.def_fsm_char_pattern(' ', r'[\\t ]*\\n?') # empty line
        Tokenizer.def_fsm_char_pattern('#', r'#[^\\n]*\\n') # comment line
        Tokenizer.def_fsm_char_pattern('L', r'[^#].*[^\\t ]+.*\\n') # other line

    Once FSM character patterns are defined, an item obtained from buffer may
    be transformed to FSM character with `fsm_char()`. There is also
    `_make_fsm_str_by_patterns()` method which uses this function to 
    map strings of buffer items into FSM strings via pattern matching. This
    method may be assigned to buffer's ``_make_fsm_str`` attribute to delegate
    creation of FSM strings to the tokenizer and use pattern-based
    implementation as below

    .. python::
        from ezmlex.buffers import LineOrientedBuffer
        from ezmlex.tokenizers import TokenizerBase

        class Buffer(LineOrientedBuffer): pass

        class Tokenizer(TokenizerBase):
            ...

        Buffer._make_fsm_str = Tokenizer._make_fsm_str_by_patterns

    **Tokens**

    The main part of lexical grammar definition is the definition of tokens.
    To define new token type it is necessary to provide its name and the
    pattern for token recognition. Each tokenizer class holds its own
    dictionary of defined token types. Note, that it is the FSM string which is
    matched against token patterns and FSM string is not necessarily equal to
    the original input string.

    Token types may be defined using `def_token_type()` class method. An
    already defined token may be then retrieved by `token_type()` class method.
    The dictionary of all defined token types may be retrieved via
    `token_types()`. Finally token type may be removed from the dictionary with
    `del_token_type()`.

    **Example** defining tokens

    .. python::
        
        from ezmlex.tokenizers import TokenizerBase
        ...
        class Tokenizer(TokenizerBase):
            ...
        Tokenizer.def_token_type('Identifier', r'[a-zA-Z]+')
        Tokenizer.def_token_type('Integer', r'[+-]?\\d+')
        Tokenizer.def_token_type('Float', r'[+-]?\\d*(?:\\.\\d+)?')

    Note, than you may use helper patterns (described below) instead of
    bare regular expressions.


    **Error types**

    If tokenizer is not able to recognize a token at some position in text it
    starts to match this text against separate set of expressions to determine
    the type of error that should be returned to user. For this purpose
    a separate dictionary of token types, i.e error tokens, is maintained by
    tokenizer class. Error token types should be defined in pretty similar way
    as normal tokens. 
    
    A new error type is defined with `def_error_type()`. An already registered
    error type may be retrieved with `error_type()`. A dictionary of all
    already defined error types is obtained from `error_types()`. Single error
    type might be removed from dictionary with `del_error_type()`.

    **Example** defining error types

    .. python::
        
        from ezmlex.tokenizers import TokenizerBase
        ...
        class Tokenizer(TokenizerBase):
            ...
        Tokenizer.def_error_type('Unrecognized',r'\\0', 'unrecognized item')
        Tokenizer.def_error_type('SyntaxError',r'[^\\0]', 'syntax error')


    Error tokens enter the sequence of output tokens same way as ordinary
    tokens. They may be distinguished from regular tokens by ``is_error()``
    method.

    **Helper patterns**

    The `TokenizerBase` class has also utilities to register general-purpose
    helper patterns (regular expressions) which may be later used to construct
    FSM character classifiers, token patterns, and error token patterns.
    An already defined pattern may be retrieved with `pattern()`. The
    dictionary of all defined patterns may be retrieved with `patterns()` class
    method. The patterns may be removed from internal dictionary with
    `del_pattern()`. Each new class derived from `TokenizerBase` has its own
    dictionary of helper patterns.
    

    **Example** Defining helper patterns

    .. python::

        from ezmlex.tokenizers import TokenizerBase
        from ezmlex.patterns import ccat

        class Tokenizer(TokenizerBase):
            ... 

        Tokenizer.def_pattern('hex', '[+-]?0[xX][a-fA-F0-9]+')
        Tokenizer.def_pattern('dec', '[+-]?[0-9]+')
        ...
        num = ccat( Tokenizer.pattern('hex'),r'|',Tokenizer.pattern('dec'))
        Tokenizer.def_token_type('num', num)

    **Complete examples**

    **Example** decompose text into words, punctuators and whitespaces
    
    .. python::

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
            Tokenizer.def_token_type('Separator',   r'[ \\t\\n]+')
            Tokenizer.def_token_type('Punctuator',  r'[\\.,;:-]')
            Tokenizer.def_error_type('SyntaxError', r'[^ \\t\\n]+','syntax error')

            # Input string
            _input = \"\"\"Lorem ipsum dolor sit amet, consectetur adipiscing
            elit. Sed aliquet odio quis elit aliquet eu interdum justo
            adipiscing. #% Vestibulum sodales ornare adipiscing.\"\"\"

            # Tokenizer instance
            tokenizer = Tokenizer(_input)

            # Recognize tokens
            for token in iter(tokenizer):
                if token.is_error():
                    print \"%d:%d:Error:%s:%r\" \\
                      % (token.line_no(), token.col_no(), token.message(), token.value())
                else:
                    print \"%d:%d:%s:%r\" \\
                      % (token.line_no(), token.col_no(), token.id(), token.value())

    The example may be found in ``examples/apidoc/TokenizerBase1.py``. The
    output from above script shall be::

        0:0:Word:'Lorem'
        0:5:Separator:' '
        0:6:Word:'ipsum'
        0:11:Separator:' '
        0:12:Word:'dolor'
        0:17:Separator:' '
        0:18:Word:'sit'
        0:21:Separator:' '
        0:22:Word:'amet'
        0:26:Punctuator:','
        0:27:Separator:' '
        0:28:Word:'consectetur'
        0:39:Separator:' '
        0:40:Word:'adipiscing'
        0:50:Separator:'\\n'
        1:0:Word:'elit'
        1:4:Punctuator:'.'
        1:5:Separator:' '
        1:6:Word:'Sed'
        1:9:Separator:' '
        1:10:Word:'aliquet'
        1:17:Separator:' '
        1:18:Word:'odio'
        1:22:Separator:' '
        1:23:Word:'quis'
        1:27:Separator:' '
        1:28:Word:'elit'
        1:32:Separator:' '
        1:33:Word:'aliquet'
        1:40:Separator:' '
        1:41:Word:'eu'
        1:43:Separator:' '
        1:44:Word:'interdum'
        1:52:Separator:' '
        1:53:Word:'justo'
        1:58:Separator:'\\n'
        2:0:Word:'adipiscing'
        2:10:Punctuator:'.'
        2:11:Separator:' '
        2:12:Error:syntax error:'#%'
        2:14:Separator:' '
        2:15:Word:'Vestibulum'
        2:25:Separator:' '
        2:26:Word:'sodales'
        2:33:Separator:' '
        2:34:Word:'ornare'
        2:40:Separator:' '
        2:41:Word:'adipiscing'
        2:51:Punctuator:'.'

    """

    @classmethod
    def patterns(cls):
        """Return helper patterns registered within tokenizer subclass.
        
        This method returns a dictionary of helper patterns registered within
        tokenizer class. If the dictionary doesn't exist it is created (empty)
        and returned.

        A pattern dictionary is a dictionary of the form

        .. python::

            _patterns = {
                'key_a' : regex_a,
                'key_b' : regex_b,
                ...
            }

        where ``key_a``, ``key_b``, ``..`` keys are mapped onto compiled
        regular expressions. Entries of `patterns()` may be easilly managed
        with following methods:

            - `def_pattern()`
            - `del_pattern()`
            - `pattern()`

        The pattern dictionary is stored as static class attribute ``_patterns``
        in a `cls` subclass.

        :Note:

            As a side effect, this method may create empty dictionary
            ``_patterns`` within ``cls`` subclass of `TokenizerBase`.
        """
        try: 
            return cls._patterns
        except AttributeError:
            cls._patterns = {}
            return cls._patterns

    @classmethod
    def def_pattern(cls, *args):
        """Register new helper pattern within tokenizer.
        
        :Parameters:
            args
                arguments and their meaning are same as for
                `ezmlex.patterns.def_pattern()`,
                except that there must be no ``tab`` argument in 
                ``*args`` list, and the ``*args`` list must start from ``_id``.
        :Note:

            If it doesn't exist, this method will create the dictionary
            ``_patterns`` within ``cls`` subclass (as a class attribute).

        :Note:

            This method may throw exceptions in case the pattern was already
            registered. For exception specification, see documentation of
            `ezmlex.patterns.def_pattern()`.
        """
        from ezmlex.patterns import def_pattern
        def_pattern(cls.patterns(), *args)

    @classmethod
    def del_pattern(cls, *args):
        """Delete previously registered helper pattern from the tokenizer.
        
        :Parameters:
            args
                arguments and their meaning are same as for
                `ezmlex.patterns.del_pattern()`,
                except that there must be no ``tab`` argument in 
                ``*args`` list, and the ``*args`` list must start from ``_id``.

        :Note:

            If it doesn't exist, this method will create empty dictionary
            ``_char_classes`` within ``cls`` subclass (as a class attribute).
                
        :Note:

            This method may throw exceptions in case the requested pattern was
            not registered. For exception specification, see documentation of
            `ezmlex.patterns.del_pattern()`.
        """
        from ezmlex.patterns import del_pattern
        del_pattern(cls.patterns(), *args)

    @classmethod
    def pattern(cls, *args):
        """Return a helper pattern registered within tokenizer.

        :Parameters:
            args 
                arguments and their meaning are same as for
                `ezmlex.patterns.pattern()`,
                except that there must be no ``tab`` argument in 
                ``*args`` list, and the ``*args`` list must start from ``_id``.

        :Note:

            If it doesn't exist, this method will create empty dictionary
            ``_char_classes`` within ``cls`` subclass (as a class attribute).

        :Note:

            This method may throw exceptions in case the requested pattern was
            not registered. For exception specification, see documentation of
            `ezmlex.patterns.pattern()`.
        """
        from ezmlex.patterns import pattern
        return pattern(cls.patterns(), *args)
    @classmethod
    def fsm_char_patterns(cls):
        """Return fsm character patterns registered within tokenizer subclass.

        This method returns a dictionary of FSM character patterns registered
        within tokenizer class. If the dictionary doesn't exist it is created
        (empty) and returned.

        A FSM character pattern dictionary is a dictionary of the form 

        .. python::

            _fsm_char_patterns = {
                'A' : regex_A,
                'B' : regex_B,
                ...
            }
        
        stored as a class attribute of `cls` subclass, where ``A``, ``B``,
        ``..`` keys are FSM characters and ``regex_A``, ``regex_B`` are
        patterns used to clasify input items and convert to FSM characters.
        Entries of `fsm_char_patterns()` may be easilly managed with following
        methods:

            - `def_fsm_char_pattern()`: register new FSM character pattern
            - `del_fsm_char_pattern()`: delete registered FSM character pattern
            - `fsm_char_pattern()`: get registered FSM character pattern

        The FSM character pattern dictionary is stored as static class
        attribute ``_fsm_char_patterns`` in a `cls` subclass.

        :Note:
            
            FSM character patterns must not overlap. If one character class
            within tokenizer matches given item, no other pattern in the
            same tokenizer may match this item.

        :Note:

            As a side effect, this method may create empty dictionary
            ``_fsm_char_patterns`` within ``cls`` subclass of `TokenizerBase`.
        """
        try: 
            return cls._fsm_char_patterns
        except AttributeError:
            cls._fsm_char_patterns = {}
            return cls._fsm_char_patterns

    @classmethod
    def def_fsm_char_pattern(cls, ch, regex, *args):
        """Register new FSM character pattern within tokenizer.
        
        :Parameters:
            ch : str
                the FSM character
            regex 
                regular expression matching all characters from the class,
                it may be either string describing regular expression or
                a regular expression object compiled with ``re.compile()``.
                See documentation of
                `ezmlex.patterns.def_pattern()` for details.
        :Note:
            
            FSM character patterns must not overlap. If one character class
            within tokenizer matches given item, no other pattern in the
            same tokenizer may match this item.

        :Note:

            If it doesn't exist, this method will create the dictionary
            ``_fsm_char_patterns`` within ``cls`` subclass (as a class
            attribute).

        :Note:

            This method may throw exceptions in case the `ch` was already
            registered. For exception specification, see documentation of
            `ezmlex.patterns.def_pattern()`.
        """
        from ezmlex.patterns import def_pattern, ccat
        if ch == '\0':
            raise RuntimeError('FSM char %s is reserved' % ch)
        def_pattern(cls.fsm_char_patterns(), ch, ccat('^', regex, '$'), *args)

    @classmethod
    def del_fsm_char_pattern(cls, ch):
        """Delete previously registered FSM character pattern.
        
        :Parameters:
            ch : str
                the FSM character
        :Note:

            If it doesn't exist, this method will create empty dictionary
            ``_fsm_char_patterns`` within ``cls`` subclass (as a class
            attribute).
                
        :Note:

            This method may throw exceptions in case the `ch` was not
            registered. For exception specification, see documentation of
            `ezmlex.patterns.del_pattern()`.
        """
        from ezmlex.patterns import del_pattern
        del_pattern(cls.fsm_char_patterns(), ch)

    @classmethod
    def fsm_char_pattern(cls, ch):
        """Return FSM character pattren registered within tokenizer.

        :Parameters:
            ch : str
                the FSM character
        :Note:

            If it doesn't exist, this method will create empty dictionary
            ``_fsm_char_patterns`` within ``cls`` subclass (as a class
            attribute).

        :Note:

            This method may throw exceptions in case the `ch` was not
            registered. For exception specification, see documentation of
            `ezmlex.patterns.pattern()`.
        """
        from ezmlex.patterns import pattern
        return pattern(cls.fsm_char_patterns(), ch)

    @classmethod
    def match_fsm_char_patterns(cls, *args):
        from ezmlex.patterns import find_matching_patterns
        return find_matching_patterns(cls.fsm_char_patterns(), *args)

    @classmethod
    def fsm_char(cls, *args):
        chars = cls.match_fsm_char_patterns(*args)
        if len(chars) == 0:
            return '\0'
        elif len(chars) == 1:
            return chars[0]
        else:
            raise RuntimeError('internal error: FSM character patterns are ' \
                             + 'not mutually exclusive.\n' \
                             + 'Tokenizer: %r\n'\
                             + 'FSM characters: %r' % (cls, chars))

    @classmethod
    def token_types(cls):
        try:
            return cls._token_types
        except AttributeError:
            cls._token_types = {}
            return cls._token_types

    @classmethod
    def def_token_type(cls, _id, pattern, *args):
        from ezmlex.tokens import def_token
        from ezmlex.patterns import ccat
        def_token(cls.token_types(), _id, ccat(pattern), *args)

    @classmethod
    def del_token_type(cls, _id):
        from ezmlex.tokens import del_token
        del_token(cls.token_types(), _id)

    @classmethod
    def token_type(cls, _id):
        from ezmlex.tokens import token
        return token(cls.token_types(), _id)

    @classmethod
    def match_token_types(cls, *args):
        from ezmlex.tokens import find_matching_tokens
        return find_matching_tokens(cls.token_types(), *args)

    @classmethod
    def error_types(cls):
        try:
            return cls._error_types
        except AttributeError:
            cls._error_types = {}
            return cls._error_types

    @classmethod
    def def_error_type(cls, _id, pattern, message, *args):
        from ezmlex.tokens import def_token, token
        from ezmlex.patterns import ccat
        tab = cls.error_types()
        def_token(tab, _id, pattern, _id, *args)
        token(tab, _id).is_error = lambda cls : True
        token(tab, _id).message = lambda cls : message

    @classmethod
    def del_error_type(cls, _id):
        from ezmlex.tokens import del_token
        del_token(cls.error_types(), _id)

    @classmethod
    def error_type(cls, _id):
        from ezmlex.tokens import token
        return token(cls.error_types(), _id)

    @classmethod
    def match_error_types(cls, *args):
        from ezmlex.tokens import find_matching_tokens
        return find_matching_tokens(cls.error_types(), *args)

    def __init__(self, _input = None, line_no = 0, col_no = 0, char_no = 0):
        """Constructor.

        :Parameters:
            _input
                input to be used as a source of tokens; supported input types
                are determined by tokenizer buffer used by particular tokenizer
                class
            line_no : int
                initial value for line index 
            col_no : int
                initial value for column index 
            char_no : int
                initial value of character offset
        """
        self._init_buffer(_input, line_no, col_no, char_no)

    def line_no(self):
        """Line index of current position.
        
        Return line index of starting position of currently processed piece
        of text. Line indices are indexed starting from zero."""
        return self._get_buffer().line_no()

    def col_no(self):
        """Column index of current position.
        
        Return column index of starting position of currently processed
        piece of text. Column indices are indexed starting from zero."""
        return self._get_buffer().col_no()

    def char_no(self):
        """Character offset of current position.
        
        Return character offset of starting position of currently processed
        piece of text. Character indices are indexed starting from zero."""
        return self._get_buffer().char_no()

    def bind(self, _input):
        """Bind input to the tokenizer.
        
        The supported input types depend on tokenizer buffer used by given
        tokenizer. They usually support strings, file objects and iterable 
        objects
        
        :Parameters:
            _input 
                the input to be read in subsequent calls to `token()`    
        """
        self._get_buffer().bind(_input)

    def __iter__(self):
        tok = self.token()
        while tok is not None:
            yield tok
            tok = self.token()

    _max_lookahead = 1
    _max_iterations = 1000000
    #_max_iterations = sys.maxint

    def token(self):
        """Try to form next token from input.
        
        This function reads text from input recently bound with `bind()` and
        tries to recognize next token.
        
        :Return:
            recognized token or one of predefined error tokens (see
            `_error_token()`)
        """
        eoi = False
        buff = self._get_buffer()
        iter_counter = 0
        while iter_counter < self._max_iterations:
            iter_counter += 1
            # Assure, than there is at least _max_lookahead characters
            # in the buffer (except we are approaching end of input)
            while (not eoi) and (len(buff) < self._max_lookahead):
                eoi = (buff.extend() < buff._default_chunk)

            # If there is no content to scan, return None
            if len(buff) == 0:
                return None
                
            fsm_str = buff.fsm_str()
            fsm_str_len = len(fsm_str)

            assert(fsm_str_len == len(buff))
            assert(fsm_str_len > 0)

            # Look for tokens matching the current FSM string starting
            # at its beginning. The match_list is a list of matching
            # tokens in form [(id0, Token0, match0), (id1, Token1,
            # match1), ...], where idN is an identifier of given token,
            # TokenN is tokens's type, such that you may create instance
            # with token = TokenN(...), and matchN is MatchObject returned
            # by re.match().
            match_list = self.match_token_types(fsm_str)
            match_list_len = len(match_list)
            if match_list_len == 0:
                # If no token matches current input, then we must emit
                # error token. The _error_token() also shifts part of buffer
                # that enters the returned error token.
                return self._error_token(fsm_str)
            elif match_list_len > 0:
                # Extract lengths of match objects from match_list
                match_len_list = map(lambda m : len(m[2].group(0)), match_list)
                # How many tokens matching whole buffer?
                whole_match_count = match_len_list.count(fsm_str_len)
                if (whole_match_count == 0) or eoi:
                    # We have only tokens matching substrings of FSM string but
                    # no token matches whole string. It is, all these tokens
                    # are complete, and all of them are candidates for the
                    # token to be returned. We chose (the longest) one and
                    # return it.
                    match_len_max = max(match_len_list)
                    match_len_max_count = match_len_list.count(match_len_max)
                    if match_len_max_count > 1:
                        # If there is more than one "longest token", then this
                        # is ambiguity, and we should indicate an error.
                        # Interpret this, as incomplete token (which could be
                        # disambiguated with few more characters).
                        return self._error_token(fsm_str) 
                    elif match_len_max_count == 1:
                        index = match_len_list.index(match_len_max)
                        _id, Token, match =  match_list[index]
                        s = buff.shift(match_len_max)
                        token = Token(s.line_no(), s.col_no(), s.char_no())
                        token.set_value(s.__str__())
                        return token
                    else:
                        raise RuntimeError(
                            'internal error: unexpected situation in '\
                          + 'tokenizer: %d tokens recognized, ' \
                          + 'but %d tokens would have maximum length' \
                          % (match_list_len, match_len_max_count))
                elif whole_match_count > 0: # and not eoi
                    # read more characters from input and let the loop to try
                    # to recover complete token
                    eoi = (buff.extend() < buff._default_chunk)
                else:
                    raise RuntimeError(
                        'internal error: we found %d tokens matching whole ' \
                        'buffer (a number less than zero!)' \
                        % whole_match_count ) 
            else:
                raise RuntimeError('internal error: number of ' \
                                 + 'candidates for token less than ' \
                                 + 'zero: %d' % match_list_len)

        raise RuntimeError('internal error: loop interrupted at iteration %d' \
                         % iter_counter )

    def _error_token(self, fsm_str):
        # Return error token matching the input
        match_list = self.match_error_types(fsm_str)
        if len(match_list) > 1:
            slice_end = min(self._max_lookahead, len(fsm_str))
            raise RuntimeError('internal error: can\'t determine error ' \
                             + 'type for FSM string starting with %r.\n' \
                             + 'The matching errors are: %r.\n' \
                             + 'Revise error definitions for the tokenizer.'\
                             % (fsm_str[:slice_end], match_list) )
        elif len(match_list) < 1:
            slice_end = min(self._max_lookahead, len(fsm_str))
            raise RuntimeError('internal error: can\'t determine error ' \
                             + 'type for FSM string starting with %r.\n' \
                             + 'No matching errors found.\n' \
                             + 'Revise error definitions for the tokenizer.'\
                             % fsm_str[:slice_end] )
        else:
            _id, Error, match = match_list[0]
            s = self._get_buffer().shift(len(match.group(0)))
            token = Error(s.line_no(), s.col_no(), s.char_no())
            token.set_value(s.__str__())
            return token

    def _init_buffer(self, *args, **kw):
        raise NotImplementedError("this method is abstract")

    def _get_buffer(self):
        if not hasattr(self, '_buffer'):
            self._init_buffer()
        return self._buffer

    @classmethod
    def _make_fsm_str_by_patterns(cls, lines):
        return ''.join(map(cls.fsm_char, lines))

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
