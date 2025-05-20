import sys
import os
from antlr4 import *
from grammar.PhysicsLexer import PhysicsLexer
from grammar.PhysicsParser import PhysicsParser
from interpreting.error_listener import ThrowingErrorListener
from interpreting.SymbolCollector import SymbolCollector
from interpreting.interpreter import Interpreter
from running_simulation.engine import Particle, System
from running_simulation.simulation import Simulation
from grammar.ScopeAndVisitor import PhysicsVisitor2


def run_phys_file(path, sim=False):
    with open(path, encoding="utf-8") as f:
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

    interpreter = Interpreter()
    interpreter.symbol_table = collector.symbol_table
    interpreter.visit(tree)

    simulate = Simulation()
    dummy = System("global")

    for name, value in interpreter.variables.items():
        if isinstance(value, Particle):
            dummy.add_particle(name, value)

    if sim:
        simulate.run(dummy, interpreter.variables["$TIME"], interpreter.variables["$DELTA"])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_phys_file(sys.argv[1])
        sim = "sim" in sys.argv
        run_phys_file(sys.argv[1], sim)
    else:

        this_file = os.path.abspath(__file__)
        cwd = os.path.dirname(this_file)

        import glob
        phys_files = sorted(glob.glob(os.path.join(cwd, "etap2", "*.phys")), key=os.path.getmtime, reverse=True)

        if not phys_files:
            print("Nie znaleziono pliku .phys.")
            exit(1)

        latest = phys_files[0]
        run_phys_file(latest)
