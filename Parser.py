#Parser

#import tokenizer


class testTokenStream:
    
    reserved = {"fn", "=>", ";", ":=", "(", ")"}
    
    def __init__(self, l):
        self.l = l
    def next(self):
        return self.l[0]
    def eatName(self):
        if self.next() not in self.reserved:
            return self.l.pop(0)
        else:
            raise firstError
    def eat(self, tk):
        if self.next() == tk:
            return self.l.pop(0)
        else:
            raise secondError

# tokenStream object; behaves like the stream from the first homework

def parseFile(fileName):
    bindings = []
    stream = tokenStream(fileName)
    while stream.next() != "main":
        name = stream.eatName()
        stream.eat(":=")
        expn = parseExpn(stream)
        stream.eat(";")
        bindings.append(name, expn)
    stream.eat("main")
    stream.eat(":=")
    expn = parseExpn(stream)
    stream.eat(";")
    bindings.append(name, expn)
    stream.finish()
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
        return stream.eatName()
    
stoppers = {';', ')', 'fn'}
            
s = testTokenStream(["fn", "x", "=>", "(", "fn", "y", "=>", "y", "x", ")", "x", ";"])

print (s.l)
print (parseExpn(s))
print (s.l)

s2 = testTokenStream(["a", "b", "fn", "x", "=>", "x", ";"])

print (s2.l)
print (parseExpn(s2))
print (s2.l)

s3 = testTokenStream(["a", "b", "c", "fn", "x", "=>", "fn", "y", "=>", "x", "y", ";"])

print (s3.l)
print (parseExpn(s3))
print (s3.l)