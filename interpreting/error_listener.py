from antlr4.error.ErrorListener import ErrorListener

class ThrowingErrorListener(ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"Błąd składniowy w linii {line}, kolumna {column}: {msg}")
