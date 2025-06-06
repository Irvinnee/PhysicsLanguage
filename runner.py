from antlr4 import *
from grammar.PhysicsLexer import PhysicsLexer
from grammar.PhysicsParser import PhysicsParser
from interpreting.error_listener import ThrowingErrorListener
from interpreting.SymbolCollector import SymbolCollector
from interpreting.interpreter import Interpreter
from running_simulation.engine import Particle, System
from running_simulation.simulation import Simulation

with open("przykladowe_programy/etap1/program.phys", encoding="utf-8") as f:
    code = f.read()

input_stream = InputStream(code)
lexer = PhysicsLexer(input_stream)
tokens = CommonTokenStream(lexer)
parser = PhysicsParser(tokens)

listener = ThrowingErrorListener()

lexer.removeErrorListeners()
parser.removeErrorListeners()
lexer.addErrorListener(listener)
parser.addErrorListener(listener)

tree = parser.prog()

if listener.has_errors():
    if listener.lexer_errors:
        print("Lexer errors:")
        for err in listener.lexer_errors:
            print("   ", err)

    if listener.parser_errors:
        print("Syntax errors:")
        for err in listener.parser_errors:
            print("   ", err)

    exit(1)

collector = SymbolCollector()
walker = ParseTreeWalker()
walker.walk(collector, tree)



if collector.errors:
    print("Semantic errors:")
    for err in collector.errors:
        print("   ", err)
    exit(1)

predeclared_funcs = {
    name: {
        "ret":  meta["ret"],          # ← nowy klucz
        "params": meta["params"],
        "expr": None,
        "block": None,
        "defined": False
    }
    for name, meta in collector.functions.items()
}
predeclared_laws = {
    name: {"params": params,
           "expr": None,
           "block": None,
           "defined": False}
    for name, params in collector.laws.items()
}

interpreter = Interpreter(
    symbol_table=collector.symbol_table,
    functions={**predeclared_funcs, **predeclared_laws}
)
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


# sim.run(dummy, interpreter.variables["$TIME"], interpreter.variables["$DELTA"])
# print()

