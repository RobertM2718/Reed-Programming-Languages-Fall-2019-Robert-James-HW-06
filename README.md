# Reed-Programming-Languages-Fall-2019-Robert-James-HW-06
Authors: James & Robert McCaull (done in collaboration)

These are the submission files for HW06: Lambda Reducer

part5.lc contains all of the code we made for testing, with individual parts broken off for each of the required parts of part 5.

Reducer.sml runs all right, but it shows variable declarations and warnings that we don't want to show. We got the basis for our tokenizer code from the miniml.py parser, but we had to make a few edits, including a very important one: the original version could not chomp comments because l[0:1] is [l[0]], not [l[0], l[1]].

To reduce a .lc file, run Lmbd.py with (name of .lc file) as an additional input on the command line. Lmbd.py can be set to verbose (step-by step demonstration) mode by changing the constants at the top of the file, but we don't suggest this since it produces output that is hard to read, and takes much longer. You can also enter files one line at a time in interactive mode by leaving out the command line argument, but we don't suggest this because it is very tedious and offers no advantage over just using a file.

Our .lc files allow a single definition of the form:
    name := . . .
on each line, . . . containing a single term of lambda calculus, with the following disambiguated grammar:
<file>  -> <line> ; <file> | <line> ;
<line>  -> <name> := <expn>
        
<expn>  -> fn <name> => <expn>
         | <pJuxt>
    
<pJuxt> -> <juxt> fn <name> => <expn>
         | <juxt>
         
<juxt>  -> <t> <juxt> | <t>
<t>     -> <name> | (<expn>)
<name>  -> x | y | fact . . .
See our test files for examples.