
TEMPFILE_NAME = "tmp_transfer_file.sml"
PRINT_TYPE = "prettyPrint"
VERBOSE = False


import os
import sys
import Parser

def interpretBindings(bindings):
    """
    Converts a list of bindings into a single AST for reduction. Any bindings following the first instance of main are ignored.
    Converts the AST into a .sml file using transfer, then executes that file to reduce and print the AST. Finally, the temporary .sml file is deleted.
    """
    AST = None
    for (n, ast) in bindings[::-1]:
        if n == "main":
            AST = ast
        elif AST is not None:
            AST = ["App", ["Lam", n, AST], ast]
    if AST is not None:
        transfer(AST)
        os.system("sml " + TEMPFILE_NAME)
        os.unlink(TEMPFILE_NAME)

def interpretFile(f):
    """
    Reads a .lc file to get a list of bindings, then interprets them for reduction using interpretBindings.
    """
    bindings = Parser.parseFile(f)
    interpretBindings(bindings)
    

def astToTermString(ast):
    """
    Converts an AST in pythonic list-of-lists form to a string to be saved in a .sml file.
    """
    if ast[0] == "Lam":
        return "Lam (\"" + ast[1] + "\", " + astToTermString(ast[2]) + ")"
    elif ast[0] == "App":
        return "Juxt (" + astToTermString(ast[1]) + ", " + astToTermString(ast[2]) + ")"
    else:
        return "Name \"" + ast[1] + '"'
        

def transfer(ast):
    """
    Writes a .sml file from an AST that, when run, prints the result of subjecting the corresponding LC term to normal-order reduction.
    """
    top = "use \"Reducer.sml\";\n"
    tString = "val termToReduce = " + astToTermString(ast) + ";\n"
    if VERBOSE:
        if PRINT_TYPE == "prettyPrint":
            command = "val _ = ppReduce termToReduce;\n"
        elif PRINT_TYPE == "simplePrint":
            command = "val _ = upReduce termToReduce;\n"
    else:
        command = "val tempVar = reduce termToReduce;\n(print (prettyString tempVar \"\"); print \"\\n\");\n"
    end = "OS.Process.exit(OS.Process.success);"
    with open(TEMPFILE_NAME, "w") as f:
        f.write(top)
        f.write(tString)
        f.write(command)
        f.write(end)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        interpretFile(sys.argv[1])
    else:
        bindings = []
        bdd = Parser.parseLine(input("-> "))
        while bdd[0] != "main":
            bindings.append(bdd)
            bdd = Parser.parseLine(input("-> "))
        bindings.append(bdd)
        interpretBindings(bindings)