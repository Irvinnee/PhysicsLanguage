from antlr4 import *
from PhysicsLexer import PhysicsLexer
from PhysicsParser import PhysicsParser
from error_listener import ThrowingErrorListener
from SymbolCollector import SymbolCollector
from interpreter import Interpreter
from running_simulation.engine import Particle, System
from running_simulation.simulation import Simulation

with open("program.phys", encoding="utf-8") as f:
    code = f.read()

input_stream = InputStream(code)
lexer = PhysicsLexer(input_stream)
tokens = CommonTokenStream(lexer)
parser = PhysicsParser(tokens)

listener = ThrowingErrorListener()
parser.removeErrorListeners()
parser.addErrorListener(listener)

tree = parser.prog()

if listener.errors:
    print("Program zawiera błędy składniowe:")
    for err in listener.errors:
        print("   ", err)
    exit(1)

collector = SymbolCollector()
walker = ParseTreeWalker()
walker.walk(collector, tree)

if collector.errors:
    print("Błędy semantyczne:")
    for err in collector.errors:
        print("   ", err)
    exit(1)

interpreter = Interpreter()
interpreter.symbol_table = collector.symbol_table
interpreter.visit(tree)

# if "cz1" in interpreter.variables and isinstance(interpreter.variables["cz1"], Particle):
#     dummy = System("global")
#     cz1 = interpreter.variables["cz1"]
#     dummy.add_particle("cz1", cz1)
#
#     sim = Simulation()
#     sim.run(dummy, 30)


sim = Simulation()
dummy = System("global")

for name, value in interpreter.variables.items():
    if isinstance(value, Particle):
        dummy.add_particle(name, value)


sim.run(dummy, 30)

print("\nFinalny stan zmiennych:")
for k, v in interpreter.variables.items():
    print(f"   {k} = {v}")
