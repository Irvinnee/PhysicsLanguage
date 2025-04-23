from antlr4.error.ErrorListener import ErrorListener

class ThrowingErrorListener(ErrorListener):
    def __init__(self):
        self.lexer_errors = []
        self.parser_errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        src_name = recognizer.__class__.__name__
        error_msg = f"[{src_name}] Linia {line}, kolumna {column}: {msg}"
        if "Lexer" in src_name:
            self.lexer_errors.append(error_msg)
        else:
            self.parser_errors.append(error_msg)

    def has_errors(self):
        return bool(self.lexer_errors or self.parser_errors)
