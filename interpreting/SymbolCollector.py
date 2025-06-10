from typing import Dict

from grammar.PhysicsListener import PhysicsListener

class Scope:
    def __init__(self, parent=None, node_type="block", ctx=None, errors=None):
        self.symbol_table: dict[str, str] = {}
        self.parent = parent
        self.children: list[Scope] = []
        self.node_type = node_type
        self.ctx = ctx
        self.errors = errors if errors is not None else []
        self.next_child_index = 0

        self.variables: Dict[str, object] = {}
        self.functions: Dict[str, Dict] = {}

    def declare(self, name, typ, line):
        if name in self.symbol_table:
            self.errors.append(f"Redeclared identifier '{name}' (line {line})")
        else:
            self.symbol_table[name] = typ

    def lookup(self, name):
        scope = self
        while scope:
            if name in scope.symbol_table:
                return scope
            scope = scope.parent
        return None

    def print_tree(self, indent=0):
        pad = "  " * indent
        print(f"{pad}- Scope ({self.node_type}): {list(self.symbol_table.keys())}")
        for child in self.children:
            child.print_tree(indent + 1)

        # TODO: ew błędy poza indexem
    def get_next_child(self):
        self.next_child_index = 0
        return self.children[self.next_child_index - 1]

    def get_parent(self):
        return self.parent


class SymbolCollector(PhysicsListener):
    def __init__(self):
        self.errors = []
        self.symbol_table = {"$TIME": "float", "$DELTA": "float"}
        self.functions: dict[str, dict] = {}
        self.laws: dict[str, list] = {}

        self.root_scope = Scope(node_type="global", errors=self.errors)
        self.root_scope.variables = {"$TIME": 10.0, "$DELTA": 1.0}
        self.current_scope = self.root_scope

    def enterDeclStmt(self, ctx):
        name, typ = ctx.ID().getText(), ctx.type_().getText()
        self.current_scope.declare(name, typ, ctx.start.line)

        if self.current_scope == self.root_scope:
            self.symbol_table[name] = typ

    def enterSystemDecl(self, ctx):
        name = ctx.ID().getText()
        if name in self.symbol_table:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
        else:
            self.symbol_table[name] = "system"

        new_scope = Scope(parent=self.current_scope, node_type="system", ctx=ctx, errors=self.errors)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        ctx.scope = new_scope

    def exitSystemDecl(self, ctx):
        self.current_scope = self.current_scope.parent

    def enterFuncDecl(self, ctx):
        name = ctx.ID().getText()
        ret_type = ctx.returnType().getText() if ctx.returnType() else "void"
        params = [(p.ID().getText(), p.type_().getText())
                  for p in (ctx.paramList().param() if ctx.paramList() else [])]

        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self.errors.append(f"Duplicate parameter '{dup}' in function '{name}' (line {ctx.start.line})")
        elif name in self.symbol_table or name in self.functions or name in self.laws:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
        else:
            self.functions[name] = {"ret": ret_type, "params": params}
            self.symbol_table[name] = "function"

        new_scope = Scope(parent=self.current_scope, node_type="func", ctx=ctx, errors=self.errors)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        ctx.scope = new_scope

        for pname, ptype in params:
            self.current_scope.declare(pname, ptype, ctx.start.line)

    def exitFuncDecl(self, ctx):
        self.current_scope = self.current_scope.parent

    def enterLawDecl(self, ctx):
        name = ctx.ID().getText()
        params = [(p.ID().getText(), p.type_().getText())
                  for p in (ctx.paramList().param() if ctx.paramList() else [])]

        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self.errors.append(f"Duplicate parameter '{dup}' in law '{name}' (line {ctx.start.line})")
        elif name in self.symbol_table or name in self.functions or name in self.laws:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
        else:
            self.laws[name] = params
            self.symbol_table[name] = "law"

        new_scope = Scope(parent=self.current_scope, node_type="law", ctx=ctx, errors=self.errors)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        ctx.scope = new_scope

        for pname, ptype in params:
            self.current_scope.declare(pname, ptype, ctx.start.line)

    def exitLawDecl(self, ctx):
        self.current_scope = self.current_scope.parent

    def enterParticleDecl(self, ctx):
        name = ctx.ID().getText()
        if name in self.symbol_table:
            self.errors.append(f"Line {ctx.start.line}: Redeclaration of variable '{name}'")
        else:
            self.symbol_table[name] = "particle"

    def print_scope_tree(self):
        self.root_scope.print_tree()

    def enterBlock(self, ctx):
        new_scope = Scope(parent=self.current_scope,
                          node_type="block",
                          ctx=ctx,
                          errors=self.errors)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        ctx.scope = new_scope

    def exitBlock(self, ctx):
        self.current_scope = self.current_scope.parent
