from __future__ import annotations

from PhysicsVisitor import PhysicsVisitor
from PhysicsParser import PhysicsParser
from running_simulation.engine import Particle, Field, System, Law


class Interpreter(PhysicsVisitor):
    def __init__(self) -> None:
        self.variables: dict[str, object] = {"$TIME": 0}
        self.symbol_table = {}
        self.global_laws: list[Law] = []
        self.functions: dict[str, dict] = {}
        self.in_function: bool = False
        self.return_value = None

    def visitProg(self, ctx):
        return self.visitChildren(ctx)


    

    def visitAssignStmt(self, ctx):
        value = self.visit(ctx.expr())
        target_ctx = ctx.target()

        if isinstance(target_ctx, PhysicsParser.VarTargetContext):
            name = target_ctx.getText()
            if name == "$TIME":
                self.variables["$TIME"] = value
            else:
                self.variables[name] = value

        elif isinstance(target_ctx, PhysicsParser.AttrTargetContext):
            obj, attr, index = self.visit(target_ctx)
            if index is not None:
                getattr(obj, attr)[index] = value
            else:
                setattr(obj, attr, value)
        # else:
        #     print(" Nieznany typ targetu")
        return None
    
    def visitDeclStmt(self, ctx):
        name = ctx.ID().getText()
        typ = ctx.type_().getText() if ctx.type_() else None

        if typ == "particle":
            self.variables[name] = Particle()
        elif typ == "field":
            self.variables[name] = Field()
        elif typ == "system":
            self.variables[name] = System()
        else:
            self.variables[name] = None

        if ctx.expr():
            self.variables[name] = self.visit(ctx.expr())


        # dodaj do systemu jeśli jesteśmy w zagnieżdżonym scope
        if "$SYSTEM" in self.variables and isinstance(self.variables["$SYSTEM"], System):
            system = self.variables["$SYSTEM"]
            if typ == "particle":
                system.add_particle(name, self.variables[name])
            elif typ == "field":
                system.add_field(name, self.variables[name])

        
        print(f"Zmienna zadeklarowana: {name} = {self.variables[name]}")
        print(f"Stan zmiennych: {self.variables}")
        return None


    def visitFuncDecl(self, ctx):
        name = ctx.ID().getText()
        params = (
            [p.ID().getText() for p in ctx.paramList().param()]
            if ctx.paramList()
            else []
        )
        self.functions[name] = {
            "params": params,
            "expr": ctx.expr() if ctx.expr() else None,
            "block": ctx.block() if ctx.block() else None,
        }
        return None
    
    def visitLawAssignStmt(self, ctx):
        target_name = ctx.dottedID().getText()
        law_name = ctx.ID().getText()
        # print(f" Rejestruję prawo {law_name} do {target_name}")

        law_meta = self.functions.get(law_name)
        if not law_meta:
            raise Exception(f"Prawo '{law_name}' nie zostało zdefiniowane")

        fn = self._wrap_fn(law_meta)
        target_obj = self.variables.get(target_name)

        if isinstance(target_obj, System):
            # przypisujemy do całego układu – działa na wszystkie particle
            target_obj.register_law(Law(fn=fn, scope=target_name, target="particle"))

        elif isinstance(target_obj, Particle):
            # przypisujemy globalnie – tylko do tej cząstki
            self.global_laws.append(Law(fn=fn, scope=target_name, target="particle"))

        else:
            raise Exception(f"Obiekt '{target_name}' nie jest systemem ani cząstką")

    def visitSystemDecl(self, ctx):
        name = ctx.ID().getText()
        system = System(name)
        self.variables[name] = system

        #  ustaw jako "aktywny system" na czas jego bloku
        prev_active = self.variables.get("$SYSTEM")
        self.variables["$SYSTEM"] = system

        self.visit(ctx.block())

        # przywróć poprzedni system (jeśli był zagnieżdżony)
        self.variables["$SYSTEM"] = prev_active
        return None

    def visitLawDecl(self, ctx):
        name = ctx.ID().getText()
        params = (
            [p.ID().getText() for p in ctx.paramList().param()]
            if ctx.paramList()
            else []
        )

        # Zapamiętaj prawo dla późniejszych przypisań <x & prawo>
        self.functions[name] = {
            "params": params,
            "expr": None,
            "block": ctx.block(),
        }


        # print(f"Zdefiniowano prawo: {name}")

        return None

    def _wrap_fn(self, meta):
        def fn(obj, system, dt):
            saved_vars = self.variables
            self.variables = saved_vars.copy()
            self.variables[meta["params"][0]] = obj
            self.visit(meta["block"])
            self.variables = saved_vars
        return fn



    def _call(self, name: str, args: list):
        # print(f" Wywołanie prawa/funkcji '{name}' z argumentami: {args}")
        if name not in self.functions:
            raise Exception(f"Nieznana funkcja {name}")

        sig = self.functions[name]
        if len(args) != len(sig["params"]):
            raise Exception(
                f"{name}: oczekiwano {len(sig['params'])} argumentów, otrzymano {len(args)}"
            )

        saved_vars = self.variables
        self.variables = saved_vars.copy()
        for p, v in zip(sig["params"], args):
            self.variables[p] = v

        self.in_function, self.return_value = True, None
        try:
            res = (
                self.visit(sig["expr"])
                if sig["expr"]
                else (self.visit(sig["block"]) or self.return_value)
            )
        finally:
            self.variables = saved_vars
            self.in_function, self.return_value = False, None
        return res

    def visitBlock(self, ctx):
        for st in ctx.statement():
            self.visit(st)
            if self.in_function and self.return_value is not None:
                break
        return None
    
    def visitAttrTarget(self, ctx):
        obj_name = ctx.dottedID().getText()
        attr_name = ctx.ID().getText()
        obj = self.variables[obj_name]

        if ctx.expr():  # czyli np. velocity[0]
            index = self.visit(ctx.expr())
            return (obj, attr_name, index)
        else:
            return (obj, attr_name, None)


    def visitIfStmt(self, ctx):
        cond = self.visit(ctx.expr(0))
        if cond:
            self.visit(ctx.block(0))
            return None

        n_conds = len(ctx.expr())
        n_blocks = len(ctx.block())

        for i in range(1, n_conds):
            cond = self.visit(ctx.expr(i))
            if cond:
                self.visit(ctx.block(i))
                return None

        if n_blocks > n_conds:
            self.visit(ctx.block(n_blocks - 1))

        return None

    def visitWhileStmt(self, ctx):
        while self.visit(ctx.expr()):
            self.visit(ctx.block())
            self.variables["$TIME"] += 1
        return None

    def visitForStmt(self, ctx):
        var_name = ctx.ID().getText()
        start_val = self.visit(ctx.expr(0))
        end_val = self.visit(ctx.expr(1))
        step_val = self.visit(ctx.expr(2))

        i = start_val
        cmp = (lambda a, b: a <= b) if step_val >= 0 else (lambda a, b: a >= b)
        while cmp(i, end_val):
            self.variables[var_name] = i
            self.visit(ctx.block())
            self.variables["$TIME"] += 1
            i += step_val
        return None

    def visitForeachStmt(self, ctx):
        var_name = ctx.ID(0).getText()
        system_name = ctx.ID(1).getText()

        system_obj = self.variables.get(system_name)
        if not isinstance(system_obj, System):
            raise Exception(f"'{system_name}' nie jest Systemem")

        for _, particle in system_obj.particles.items():
            self.variables[var_name] = particle
            self.visit(ctx.block())
            self.variables["$TIME"] += 1
        return None

    def visitReturnStmt(self, ctx):
        self.return_value = self.visit(ctx.expr())
        return self.return_value

    def visitPrintStmt(self, ctx):
        print(self.visit(ctx.expr()))
        return None

    def visitExpr(self, ctx): return self.visit(ctx.logicOr())

    def visitLogicOr(self, ctx):
        res = self.visit(ctx.logicAnd(0))
        for i in range(1, len(ctx.logicAnd())):
            res = res or self.visit(ctx.logicAnd(i))
        return res

    def visitLogicAnd(self, ctx):
        res = self.visit(ctx.equality(0))
        for i in range(1, len(ctx.equality())):
            res = res and self.visit(ctx.equality(i))
        return res

    def visitEquality(self, ctx):
        left = self.visit(ctx.compare(0))
        if len(ctx.compare()) == 1:
            return left

        op = ctx.getChild(1).getText()
        right = self.visit(ctx.compare(1))
        return {
            "==": left == right,
            "!=": left != right,
            ">": left > right,
            "<": left < right,
            ">=": left >= right,
            "<=": left <= right,
        }[op]

    def visitCompare(self, ctx): return self.visit(ctx.addSub())

    def visitAddSub(self, ctx):
        res = self.visit(ctx.mulDiv(0))
        for i in range(1, len(ctx.mulDiv())):
            op = ctx.getChild(2 * i - 1).getText()
            val = self.visit(ctx.mulDiv(i))
            res = res + val if op == "+" else res - val
        return res

    def visitMulDiv(self, ctx):
        res = self.visit(ctx.power(0))
        for i in range(1, len(ctx.power())):
            op = ctx.getChild(2 * i - 1).getText()
            val = self.visit(ctx.power(i))
            res = res * val if op == "*" else res / val
        return res

    def visitPower(self, ctx):
        res = self.visit(ctx.unary(0))
        for i in range(1, len(ctx.unary())):
            res **= self.visit(ctx.unary(i))
        return res

    def visitUnary(self, ctx):
        if ctx.getChildCount() == 3 and ctx.getChild(1).getText() == '?':
            obj_name = ctx.dottedID().getText()
            attr_name = ctx.ID().getText()
            obj = self.variables[obj_name]
            return hasattr(obj, attr_name)

        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            val = self.visit(ctx.unary())
            return {"Not": lambda x: not x, "-": lambda x: -x, "+": lambda x: +x}[op](val)

        return self.visit(ctx.atom())

    def visitVector(self, ctx): return [self.visit(e) for e in ctx.expr()]

    def visitAtom(self, ctx):
        if ctx.INT():
            return int(ctx.INT().getText())
        if ctx.FLOAT():
            return float(ctx.FLOAT().getText())
        if ctx.vector():
            return self.visit(ctx.vector())

        if ctx.getChild(0).getText() == "(":
            return self.visit(ctx.expr())

        text = ctx.getText()

        # --- Funkcja z nawiasami np. f(x)
        if "(" in text:
            func_name = ctx.dottedID().getText()
            args = [self.visit(a) for a in ctx.argList().expr()] if ctx.argList() else []
            return self._call(func_name, args)

        # --- Atrybut: obiekt->pole lub obiekt->pole[i]
        if "->" in text:
            obj_name, rest = text.split("->", 1)
            obj = self.variables[obj_name]
            if "[" in rest:
                attr, idx_txt = rest[:-1].split("[")
                return getattr(obj, attr)[int(idx_txt)]
            return getattr(obj, rest)

        # --- Użycie zmiennej: sprawdzamy symbol_table
        if text in self.symbol_table:
            return self.variables[text]

        # --- wyjątek dla specjalnych zmiennych
        if text.startswith("$") and text in self.variables:
            return self.variables[text]

        raise Exception(f"Use of undeclared variable '{text}'")


    def visitSystemAddStmt(self, ctx):
        system_name = ctx.dottedID().getText()
        particle_name = ctx.ID().getText()

        system = self.variables.get(system_name)
        particle = self.variables.get(particle_name)

        if not isinstance(system, System):
            raise Exception(f"'{system_name}' nie jest Systemem")
        if not isinstance(particle, Particle):
            raise Exception(f"'{particle_name}' nie jest Particle")

        system.add_particle(particle_name, particle)

        return None

    def visitCall(self, ctx):
        func_name = ctx.dottedID().getText()
        args = [self.visit(a) for a in ctx.argList().expr()] if ctx.argList() else []

        if func_name == "run":
            if len(args) not in (2, 3):
                raise Exception("run(system/particle, steps [, dt])")

            dt = float(args[2]) if len(args) == 3 else 1.0
            steps = int(args[1])

            obj = args[0]

            if isinstance(obj, System):
                for _ in range(steps):
                    obj.laws += self.global_laws
                    obj.step(dt)
                    self.variables["$TIME"] = obj.time
                return None

            if isinstance(obj, Particle):
                name = None
                for var_name, var_obj in self.variables.items():
                    if var_obj is obj:
                        name = var_name
                        break
                if name is None:
                    raise Exception("Nie udało się ustalić nazwy cząstki")

                for _ in range(steps):
                    for law in self.global_laws:
                        if law.applies(name, obj):
                            law.fn(obj, None, dt)
                    for i in range(3):
                        obj.position[i] += obj.velocity[i] * dt
                    self.variables["$TIME"] += dt
                return None


            else:
                raise Exception("pierwszy argument run() musi być Systemem albo Particle")

        # pozostałe wywołania
        self._call(func_name, args)
        return None
