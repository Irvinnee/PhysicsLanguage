from grammar.PhysicsListener import PhysicsListener

class SymbolCollector(PhysicsListener):
    def __init__(self):
        self.symbol_table = {"$TIME": "float", "$DELTA": "float"}
        self.functions: dict[str, dict] = {}
        self.laws:      dict[str, list] = {}
        self.errors:    list[str]       = []

        self.scope_stack: list[set[str]] = [set()]   # ← global

    # ─────────── pomocnicze ──────────────────────────────────────────
    def _current(self) -> set[str]:
        return self.scope_stack[-1]

    # ───────── zmienne / systemy ─────────────────────────────────────
    def enterDeclStmt(self, ctx):
        name, typ = ctx.ID().getText(), ctx.type_().getText()
        cur = self._current()

        if name in cur:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
            return

        cur.add(name)
        if len(self.scope_stack) == 1:          # tylko w globalnym
            self.symbol_table[name] = typ

    def enterSystemDecl(self, ctx):
        name = ctx.ID().getText()
        if name in self.symbol_table:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
        else:
            self.symbol_table[name] = "system"

    # ───────── funkcje ──────────────────────────────────────────────
    def enterFuncDecl(self, ctx):
        name = ctx.ID().getText()

        # 1) typ zwracany (brak ⇒ "void")
        ret_type = ctx.returnType().getText() if ctx.returnType() else "void"

        # 2) lista (nazwa, typ) parametrów
        params = [(p.ID().getText(), p.type_().getText())
                  for p in (ctx.paramList().param() if ctx.paramList() else [])]

        # 3) walidacje
        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self.errors.append(
                f"Duplicate parameter '{dup}' in function '{name}' (line {ctx.start.line})"
            )
        elif name in self.symbol_table or name in self.functions or name in self.laws:
            self.errors.append(
                f"Redeclared identifier '{name}' (line {ctx.start.line})"
            )
        else:
            # 4) ZAPAMIĘTUJEMY  ‹ret›  +  ‹params›
            self.functions[name] = {"ret": ret_type, "params": params}

        # 5) zakładamy lokalny scope parametrów
        self.scope_stack.append(set(names_only))

    def exitFuncDecl(self, ctx):
        self.scope_stack.pop()                  # ⇠ wychodzimy ze scope’u

    # ───────── prawa fizyczne ───────────────────────────────────────
    def enterLawDecl(self, ctx):
        name = ctx.ID().getText()

        params = [(p.ID().getText(), p.type_().getText())
                  for p in (ctx.paramList().param() if ctx.paramList() else [])]

        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self.errors.append(f"Duplicate parameter '{dup}' in law '{name}' "
                               f"(line {ctx.start.line})")
        elif name in self.symbol_table or name in self.functions or name in self.laws:
            self.errors.append(f"Redeclared identifier '{name}' (line {ctx.start.line})")
        else:
            self.laws[name] = params

        self.scope_stack.append(set(n for n, _ in params))   # nowy scope

    def exitLawDecl(self, ctx):
        self.scope_stack.pop()
