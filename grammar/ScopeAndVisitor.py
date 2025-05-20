from grammar.PhysicsVisitor import PhysicsVisitor
from grammar.PhysicsParser import PhysicsParser


class Scope:
    def __init__(self, name="<unnamed>", parent=None):
        self.name = name
        self.symbols = {}
        self.parent = parent

    def define(self, name, value):
        self.symbols[name] = value

    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.resolve(name)
        return None


class PhysicsVisitor2(PhysicsVisitor):
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope

    def visitProg(self, ctx):
        result = self.visitChildren(ctx)
        return result

    def visitDeclStmt(self, ctx):
        var_type = ctx.type_().getText()
        var_name = ctx.ID().getText()
        self.current_scope.define(var_name, var_type)
        return self.visitChildren(ctx)

    def visitAssignStmt(self, ctx):
        name = ctx.target().getText()
        if not self.current_scope.resolve(name):
            print(f"Assign to undefined variable: {name}")
        else:
            print(f"Assigning to {name} in {self.current_scope.name}")
        return self.visitChildren(ctx)


