from antlr4 import *
from PhysicsLexer import PhysicsLexer
from PhysicsParser import PhysicsParser

input_stream = InputStream("Particle p = 5")

lexer = PhysicsLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = PhysicsParser(token_stream)

tree = parser.prog()


print(tree.toStringTree(recog=parser))
