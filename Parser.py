#Parser

#import tokenizer


"""
<file>  := <line> ; <file> | <>

<line>  := clear <name> 
         | add <name> from <name> 
         | <name> := <expn>
        
<expn>  := fn <name> => <expn>
         | <pJuxt>
    
<pJuxt> := <juxt> fn <name> => <expn>
         | <juxt>
         
<juxt>  := <t> <juxt> | <t>

<t>     := <name> | (<expn>)

<name>  := x | y | fact . . .
"""


#class testTokenStream:
#    
#    reserved = {"fn", "=>", ";", ":=", "(", ")"}
#    
#    def __init__(self, l):
#        self.l = l
#    def next(self):
#        return self.l[0]
#    def eatName(self):
#        if self.next() not in self.reserved:
#            return self.l.pop(0)
#        else:
#            raise firstError
#    def eat(self, tk):
#        if self.next() == tk:
#            return self.l.pop(0)
#        else:
#            raise secondError

# tokenStream object; behaves like the stream from the first homework

def parseFile(fileName):
    bindings = []
    with open(fileName, 'r') as f:
        stream = TokenStream(f.read(), fileName)
    while stream.next() != "main":
        name = stream.eatName()
        stream.eat(":=")
        expn = parseExpn(stream)
        stream.eat(";")
        bindings.append((name, expn))
    stream.eat("main")
    stream.eat(":=")
    expn = parseExpn(stream)
    stream.eat(";")
    bindings.append(("main", expn))
    stream.checkEOF()
    return bindings
#
#def parseExpn(stream):
#    return parseLam(stream)
#
#def parseLam(stream):
#    if stream.next() == "fn":
#        stream.eat("fn")
#        n = stream.eatName()
#        stream.eat("=>")
#        l = parseLam(stream)
#        return ["Lam", n, l]
#    else:
#        return parseJuxt(stream)
#    
#def parseJuxt(stream):
#    
#    elif stream.next() == "(":
#        stream.eat("(")
#        expn = parseExpn(stream)
#        stream.eat(")")
#        return expn
#    else:
#        e = parseExpn()
#        while :
#            get_juxt_terms_left_associative
#        return all of those
#        
#


def parseExpn(stream):
    #
    # <expn> := fn x => <expn> | <pJuxt>
    #
    if stream.next() == "fn":
        stream.eat("fn")
        n = stream.eatName()
        stream.eat("=>")
        e = parseExpn(stream)
        return ["Lam", n, e]
    else:
        return parsePreJuxt(stream)

def parsePreJuxt(stream): 
    #
    # <pJuxt> := <juxt> fn x => <expn> | <juxt>
    #
    j = parseJuxt(stream)
    if stream.next() == "fn":
        return ["App", j, parseExpn(stream)]
    return j

def parseJuxt(stream):
    #
    # <juxt> := <juxt> <t> | <t>
    #
    e = parseTerminal(stream)
    while not stream.next() in stoppers:
        t = parseTerminal(stream)
        e = ["App", e, t]
    return e
    
def parseTerminal(stream):
    #
    # <t> := x | (<expn>)
    #
    if stream.next() == "(":
        stream.eat("(")
        e = parseExpn(stream)
        stream.eat(")")
        return e
    else:
        return ["Var", stream.eatName()]
    
stoppers = {';', ')', 'fn'}
#            
#s = testTokenStream(["fn", "x", "=>", "(", "fn", "y", "=>", "y", "x", ")", "x", ";"])
#
#print (s.l)
#print (parseExpn(s))
#print (s.l)
#
#s2 = testTokenStream(["a", "b", "fn", "x", "=>", "x", ";"])
#
#print (s2.l)
#print (parseExpn(s2))
#print (s2.l)
#
#s3 = testTokenStream(["a", "b", "c", "fn", "x", "=>", "fn", "y", "=>", "x", "y", ";"])
#
#print (s3.l)
#print (parseExpn(s3))
#print (s3.l)

    
"""
This code is mostly from Jim's parser
"""


RESERVED = {'fn', '=>', ':=', '(', ')', ';', 'eof'}

# Characters that separate expressions.
DELIMITERS = '();'

OPERATORS = {':', '=', '>'}


#
# LEXICAL ANALYSIS / TOKENIZER
#
# The code below converts ML source code text into a sequence 
# of tokens (a list of strings).  It does so by defining the
#
#    class TokenStream
#
# which describes the methods of an object that supports this
# lexical conversion.  The key method is "analyze" which provides
# the conversion.  It is the lexical analyzer for ML source code.
#
# The lexical analyzer works by CHOMP methods that processes the
# individual characters of the source code's string, packaging
# them into a list of token strings.
#
# The class also provides a series of methods that can be used
# to consume (or EAT) the tokens of the token stream.  These are
# used by the parser.
#

class ParseError(Exception):
    pass

class SyntaxError(Exception):
    pass

class LexError(Exception):
    pass

class TokenStream:

    def __init__(self,src,filename="STDIN"):
        """
        Builds a new TokenStream object from a source code string.
        """
        self.sourcename = filename
        self.source = src # The char sequence that gets 'chomped' by the lexical analyzer.
        self.tokens = []  # The list of tokens constructed by the lexical analyzer.
        self.extents = []     
        self.starts = []

        # Sets up and then runs the lexical analyzer.
        self.initIssue()
        self.analyze()
        self.tokens.append("eof")

    #
    # PARSING helper functions
    #

    def lexassert(self,c):
        if not c:
            self.raiseLex("Unrecognized character.")

    def raiseLex(self,msg):
        s = self.sourcename + " line "+str(self.line)+" column "+str(self.column)
        s += ": " + msg
        raise LexError(s)

    def next(self):
        """
        Returns the unchomped token at the front of the stream of tokens.
        """
        return self.tokens[0]

    def advance(self):
        """ 
        Advances the token stream to the next token, giving back the
        one at the front.
        """
        tk = self.next()
        del self.tokens[0]
        del self.starts[0]
        return tk

    def report(self):
        """ 
        Helper function used to report the location of errors in the 
        source code.
        """
        lnum = self.starts[0][0]
        cnum = self.starts[0][1]
        return self.sourcename + " line "+str(lnum)+" column "+str(cnum)

    def eat(self,tk):
        """
        Eats a specified token, making sure that it is the next token
        in the stream.
        """
        if tk == self.next():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected: '"+tk+"'. "
            raise SyntaxError(err1 + err2 + err3)

    def eatName(self):
        """
        Eats a name token, making sure that such a token is next in the stream.
        """
        if self.nextIsName():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a name. "
            raise SyntaxError(err1 + err2 + err3)


    def checkEOF(self):
        """
        Checks if all the tokens were used
        """
        if self.next() != 'eof':
            raise ParseError("Parsing failed to consume tokens "+str(self.tokens[:-1])+".")


    def nextIsName(self):
        """
        Checks if next token is a name.
        """
        tk = self.next()
        isname = tk[0].isalpha() or tk[0] =='_'
        for c in tk[1:]:
            isname = isname and (c.isalnum() or c == '_')
        return isname and (tk not in RESERVED)

    #
    # TOKENIZER helper functions
    #
    # These are used by the 'analysis' method defined below them.
    #
    # The parsing functions EAT the token stream, whereas
    # the lexcial analysis functions CHOMP the source text
    # and ISSUE the individual tokens that form the stream.
    #

    def initIssue(self):
        self.line = 1
        self.column = 1
        self.markIssue()

    def markIssue(self):
        self.mark = (self.line,self.column)

    def issue(self,token):
        self.tokens.append(token)
        self.starts.append(self.mark)
        self.markIssue()

    def nxt(self,lookahead=1):
        if len(self.source) == 0:
            return ''
        else:
            return self.source[lookahead-1]

    def chompSelector(self):
        self.lexassert(self.nxt() == '#' and self.nxt(2).isdigit())
        token = self.chompChar()
        token = '#'
        while self.nxt().isdigit():
            token += self.chompChar()
        self.issue(token)

    def chompWord(self):
        self.lexassert(self.nxt().isalpha() or self.nxt() == '_')
        token = self.chompChar()
        while self.nxt().isalnum() or self.nxt() == '_':
            token += self.chompChar()
        self.issue(token)
        
    def chompComment(self):
        self.lexassert(len(self.source)>1 and self.source[0:2] == '(*')
        self.chompChar() # eat (*
        self.chompChar() #
        while len(self.source) >= 2 and self.source[0:2] != '*)':        
            self.chomp()
        if len(self.source) < 2:
            self.raiseLex("EOF encountered within comment")
        else:
            self.chompChar() # eat *)
            self.chompChar() #     

    def chomp(self):
        if self.nxt() in "\n\t\r ":
            self.chompWhitespace()
        else:
            self.chompChar()

    def chompChar(self):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        self.column += 1
        return c

    def chompWhitespace(self,withinToken=False):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        if c == ' ':
            self.column += 1
        elif c == '\t':
            self.column += 4
        elif c == '\n':
            self.line += 1
            self.column = 1
        if not withinToken:
            self.markIssue()
        
    def chompOperator(self):
        token = ''
        while self.nxt() in OPERATORS:
            token += self.chompChar()
        self.issue(token)

    #
    # TOKENIZER
    #
    # This method defines the main loop of the
    # lexical analysis algorithm, one that converts
    # the source text into a list of token strings.

    def analyze(self):
        
        while self.source != '':
            # CHOMP a comment
            if self.source[0:2] == '(*':
                self.chompComment()
            # CHOMP whitespace
            elif self.source[0] in ' \t\n\r':
                self.chompWhitespace()
            # CHOMP a single "delimiter" character
            elif self.source[0] in DELIMITERS:
                self.issue(self.chompChar())
            # CHOMP a reserved word or a name.
            elif self.source[0] in OPERATORS:
                self.chompOperator()
            else:
                self.chompWord()
