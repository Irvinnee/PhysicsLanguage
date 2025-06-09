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
import glob


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

def show_gui_before_simulation(path):
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
    import threading

    class App(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Symulacja cząsteczek")
            self.setGeometry(100, 100, 300, 150)

            layout = QVBoxLayout()
            self.label = QLabel(f"Plik: {path}")
            self.button = QPushButton("Start symulacji")
            self.button.clicked.connect(self.start_simulation)

            layout.addWidget(self.label)
            layout.addWidget(self.button)
            self.setLayout(layout)

        def start_simulation(self):
            threading.Thread(target=lambda: run_phys_file(path, sim=False)).start()
            self.close()

    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    args = sys.argv[1:]
    simulation = "True" in args

    base_dir = os.path.dirname(os.path.abspath(__file__))
    phys_file = next((arg for arg in args if arg.endswith(".phys")), None)

    if phys_file:
        full_path = os.path.join(base_dir, phys_file) if not os.path.isabs(phys_file) else phys_file
        run_phys_file(full_path, sim=simulation)
    else:
        files = sorted(glob.glob(os.path.join(base_dir, "przykladowe_programy/etap3", "*.phys")), key=os.path.getmtime, reverse=True)
        if not files:
            print("Nie znaleziono plików .phys.")
            exit(1)

        run_phys_file(files[0], sim=simulation)