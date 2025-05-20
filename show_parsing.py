from antlr4 import *
from grammar.PhysicsLexer import PhysicsLexer
from grammar.PhysicsParser import PhysicsParser
from interpreting.error_listener import ThrowingErrorListener
from textwrap import indent

with open("przykladowe_programy/etap3/fory.phys", encoding="utf-8") as f:
    code = f.read()

input_stream = InputStream(code)
lexer = PhysicsLexer(input_stream)
tokens = CommonTokenStream(lexer)
parser = PhysicsParser(tokens)

listener = ThrowingErrorListener()
parser.removeErrorListeners()
parser.addErrorListener(listener)

tree = parser.prog()
parsing = str(tree.toStringTree(recog=parser))

parsing = parsing.replace("(", "\n(").split("\n")[1:]
indent_count = 0

for line in parsing:
    print(indent(line, indent_count*"\t"))
    indent_count += line.count("(")
    indent_count -= line.count(")")