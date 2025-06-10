import sys
import os
import glob
from antlr4 import *
from grammar.PhysicsLexer import PhysicsLexer
from grammar.PhysicsParser import PhysicsParser
from interpreting.error_listener import ThrowingErrorListener
from interpreting.SymbolCollector import SymbolCollector
from interpreting.interpreter import Interpreter
from running_simulation.engine import Particle, System
from running_simulation.simulation import Simulation

def run_phys_file(path, sim=False):
    with open(path, encoding="utf-8") as f:
        code = f.read()

    # ANTLR: lexer + parser
    input_stream = InputStream(code)
    lexer = PhysicsLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = PhysicsParser(tokens)

    # Obsługa błędów składniowych
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

    # Pass 1: zbieranie symboli
    collector = SymbolCollector()
    walker = ParseTreeWalker()
    walker.walk(collector, tree)

    if collector.errors:
        print("Semantic errors:")
        for err in collector.errors:
            print("   ", err)
        exit(1)

    # Pass 2: interpretacja
    interpreter = Interpreter()
    interpreter.symbol_table = collector.symbol_table
    interpreter.visit(tree)

    # Zbieranie cząstek do systemu
    dummy = System("global")
    for name, value in interpreter.variables.items():
        if isinstance(value, Particle):
            dummy.add_particle(name, value)

    delta = interpreter.variables.get("$DELTA", 1.0)
    time_limit = interpreter.variables.get("$TIME", 10.0)
    simulate = Simulation(list(dummy.particles.values()), delta)
    simulate.global_laws = interpreter.global_laws

    if sim:
        simulate.run(dummy, time_limit, delta)
    else:
        simulate.simulate_to_time(time_limit)
        print("Pozycje po symulacji:")
        for p in simulate.particles:
            print(p.position)

if __name__ == "__main__":
    args = sys.argv[1:]
    simulation = "True" in args

    base_dir = os.path.dirname(os.path.abspath(__file__))
    phys_file = next((arg for arg in args if arg.endswith(".phys")), None)

    if phys_file:
        full_path = os.path.join(base_dir, phys_file) if not os.path.isabs(phys_file) else phys_file
        run_phys_file(full_path, sim=simulation)
    else:
        files = sorted(
            glob.glob(os.path.join(base_dir, "przykladowe_programy/etap4", "*.phys")),
            key=os.path.getmtime,
            reverse=True
        )
        if not files:
            print("Nie znaleziono plików .phys.")
            exit(1)

        run_phys_file(files[0], sim=simulation)
