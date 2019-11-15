
TEMPFILE_NAME = "tmp_transfer_file.sml"


import os
import sys
import Parser

def interpretFile(f):
    bindings = Parser.parseFile(f)
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

def astToTermString(ast):
    if ast[0] == "Lam":
        return "Lam (\"" + ast[1] + "\", " + astToTermString(ast[2]) + ")"
    elif ast[0] == "App":
        return "Juxt (" + astToTermString(ast[1]) + ", " + astToTermString(ast[2]) + ")"
    else:
        return "Name \"" + ast[1] + '"'
        

def transfer(ast):
    top = "use \"Reducer.sml\";\n"
    tString = "val termToReduce = " + astToTermString(ast) + ";\n"
    #command = "val _ = ppReduce termToReduce;\n"
    command = "val tempVar = reduce termToReduce;\n(print (prettyString tempVar \"\"); print \"\\n\");\n"
    #command = "val _ = upReduce termToReduce;\n"
    end = "OS.Process.exit(OS.Process.success);"
    with open(TEMPFILE_NAME, "w") as f:
        f.write(top)
        f.write(tString)
        f.write(command)
        f.write(end)
    
if __name__ == "__main__":
    interpretFile(sys.argv[1])