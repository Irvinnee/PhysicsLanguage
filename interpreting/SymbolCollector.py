from grammar.PhysicsListener import PhysicsListener

class SymbolCollector(PhysicsListener):
    def __init__(self):
        self.symbol_table = {"$TIME": "float"}
        self.errors = []

    def enterDeclStmt(self, ctx):
        name = ctx.ID().getText()
        typ = ctx.type_().getText()

        if name in self.symbol_table:
            self.errors.append(f"Redeclared variable '{name}' (line {ctx.start.line})")
        else:
            self.symbol_table[name] = typ

    def enterSystemDecl(self, ctx):
        name = ctx.ID().getText()
        if name in self.symbol_table:
            self.errors.append(f"Redeclared system '{name}' (line {ctx.start.line})")
        else:
            self.symbol_table[name] = "system"
