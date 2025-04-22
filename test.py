from antlr4 import *
from PhysicsLexer import PhysicsLexer
from PhysicsParser import PhysicsParser

input_stream = InputStream("""
for int xd(0,10,2):
    for int xd2(0,10,2):
        int i = 4

particle P = 5

""")

lexer = PhysicsLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = PhysicsParser(token_stream)

tree = parser.prog()


print(tree.toStringTree(recog=parser))
