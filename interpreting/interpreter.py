from __future__ import annotations

import builtins
from typing import Any, Optional, Dict, List

from grammar.PhysicsVisitor import PhysicsVisitor
from grammar.PhysicsParser import PhysicsParser
from running_simulation.engine import Particle, Field, System, Law

class Interpreter(PhysicsVisitor):
    """
    Główny interpreter języka PhysicsDSL.

    Wersja jednoprzejściowa (nagłówki funkcji i praw zbiera rozszerzony
    SymbolCollector).  Obsługuje:
      * rekordy aktywacji (rekurencja bez- i pośrednia)
      * wykrywanie redeklaracji zmiennych / funkcji / parametrów
      * sprawdzanie niezgodności typów (m.in. brak rzutowania bool → float)
      * automatyczne rzutowanie int → float przy przypisaniach
      * rozbudowany system błędów z numerem linii
    """

    # ────────────────────────────────────────────────────────────────────
    # Inicjalizacja
    # ────────────────────────────────────────────────────────────────────
    def __init__(
        self,
        symbol_table: Optional[Dict[str, str]] = None,
        functions: Optional[Dict[str, Dict]] = None,
    ) -> None:
        # Specjalne zmienne globalne
        self.variables: Dict[str, object] = {"$TIME": 10.0, "$DELTA": 1.0}

        # Tabelę symboli i wstępnie zadeklarowane funkcje/prawa
        # przekazujemy z SymbolCollector (jeśli dostarczono)
        self.symbol_table: Dict[str, Any] = symbol_table.copy() if symbol_table else {}

        # słownik funkcji: nazwa → metadane
        self.functions: Dict[str, Dict] = functions.copy() if functions else {}

        # globalne prawa fizyczne
        self.global_laws: List[Law] = []

        # flaga „czy jesteśmy wewnątrz funkcji” i ewent. wynik return
        self.in_function: bool = False
        self.return_value = None
        self.current_particle: Optional[str] = None
        self.current_system: Optional[System] = None

    # ————————————————————————————————————————————————————————————————
    # Pomocnicze narzędzia raportowania błędów
    # ————————————————————————————————————————————————————————————————

    def _error(self, ctx, message: str) -> None:
        print("Interpreter error:")
        print(f"   Line {ctx.start.line}: {message}")
        exit(0)

    def errorWrongType(self, wrong_type, right_type, variable, ctx):
        self._error(ctx, f"Assigned type {wrong_type} to variable '{variable}', should be {right_type}")

    def errorWrongAction(self, wrong_action, type_of_variable, variable_1, variable_2, ctx):
        self._error(ctx, f"Action {wrong_action} to variable '{variable_1}' and variable '{variable_2}', cannot be done on this type {type_of_variable} of variables")

    # ————————————————————————————————————————————————————————————————
    # Dwupassowe przetwarzanie programu – pass #1 kolekcjonuje wszystkie
    # deklaracje funkcji/praw, pass #2 wykonuje kod.
    # ————————————————————————————————————————————————————————————————

    def visitProg(self, ctx):
        # Pass 1 – tylko nagłówki funkcji oraz prawa
         return self.visitChildren(ctx)

    # ————————————————————————————————————————————————————————————————
    # Deklaracje zmiennych
    # ————————————————————————————————————————————————————————————————

    def visitDeclStmt(self, ctx):
        name = ctx.ID().getText()
        typ  = ctx.type_().getText() if ctx.type_() else None

        # ───── redeklaracja *tylko* gdy obiekt już istnieje ─────
        # ─ redeklaracja tylko w GLOBALU ────────────────────────────────
        if not self.in_function and name in self.variables:
            self._error(ctx, f"Redeclaration of variable '{name}'")
        # ----------------------------------------------------------------


        # jeżeli SymbolCollector wpisał już typ – sprawdź zgodność
        if name in self.symbol_table:            # pierwszy raz „na serio”
            prev = self.symbol_table[name]
            if prev not in (True, typ):          # True == brak jawnego typu
                self._error(
                    ctx,
                    f"Conflicting type for variable '{name}' "
                    f"(previous '{prev}', now '{typ}')"
                )
        else:
            self.symbol_table[name] = typ if typ else True
        # ─────────────────────────────────────────────────────────

        # Przygotuj wartość domyślną / obiekt
        if typ == "particle":
            self.variables[name] = Particle()
        elif typ == "field":
            self.variables[name] = Field()
        elif typ == "system":
            self.variables[name] = System(name)
        else:
            self.variables[name] = None

        # (reszta metody – inicjalizacja wyrażeniem, rejestracja w $SYSTEM – bez zmian)


        # Inicjalizacja ekspresją, jeśli podana.
        if ctx.expr():
            val = self.visit(ctx.expr())
            if typ == "bool" and not isinstance(val, bool):
                self._error(ctx,
                    f"Assigned type {type(val).__name__} to variable '{name}', "
                    "should be bool")

            # Zabroń rzutowania bool → float / int.
            if isinstance(val, bool) and typ in ("float", "int"):
                self.errorWrongType(type(val), typ, name, ctx)

            # Automatyczne int → float
            try:
                if typ == "int" and isinstance(val, float):
                    casted_val = round(val)
                elif typ == "float" and isinstance(val, int):
                    casted_val = float(val)
                else:
                    casted_val = val
                
                self.variables[name] = casted_val
            except (ValueError, TypeError):
                self.errorWrongType(type(val), typ, name, ctx)

        # Automatyczna rejestracja cząstek/pól w bieżącym systemie
        if "$SYSTEM" in self.variables and isinstance(self.variables["$SYSTEM"], System):
            system = self.variables["$SYSTEM"]
            if typ == "particle":
                system.add_particle(name, self.variables[name])
            elif typ == "field":
                system.add_field(name, self.variables[name])

        return None

    # ————————————————————————————————————————————————————————————————
    # Przypisania do zmiennych / atrybutów
    # ————————————————————————————————————————————————————————————————

    def visitAssignStmt(self, ctx):
        value = self.visit(ctx.expr())
        target_ctx = ctx.target()

        if isinstance(target_ctx, PhysicsParser.VarTargetContext):
            name = target_ctx.getText()

            # Przypisanie do particles w systemie
            if self.current_system and name == "particles":
                system = self.variables[self.current_system]
                if not isinstance(value, list):
                    self._error(ctx, f"'particles' must be a list")
                for item in value:
                    if isinstance(item, str):
                        if item not in self.variables or not isinstance(self.variables[item], Particle):
                            self._error(ctx, f"'{item}' is not a defined Particle")
                        particle = self.variables[item]
                    elif isinstance(item, Particle):
                        particle = item
                    else:
                        self._error(ctx, f"Invalid item in particle list: {item}")
                    system.add_particle(item if isinstance(item, str) else "", particle)
                return None

            # Przypisanie do atrybutu cząstki
            if self.current_particle:
                particle = self.variables[self.current_particle]
                if name == "pos":
                    name = "position"
                elif name == "vel":
                    name = "velocity"
                setattr(particle, name, value)
                return None

            # Specjalne zmienne globalne
            if name in ("$TIME", "$DELTA"):
                if not isinstance(value, (int, float)):
                    self.errorWrongType(type(value), (float, int), name, ctx)
                self.variables[name] = value
                return None

            # Sprawdzenie, czy zmienna była zadeklarowana
            if name not in self.symbol_table:
                self._error(ctx, f"Assignment to undeclared variable '{name}'")

            declared_type = self.symbol_table[name]

            if declared_type == "bool" and not isinstance(value, bool):
                self.errorWrongType(type(value).__name__, "bool", name, ctx)

            if isinstance(value, bool) and declared_type in ("float", "int"):
                self.errorWrongType(type(value).__name__, declared_type, name, ctx)

            try:
                if declared_type == "int" and isinstance(value, float):
                    casted_val = round(value)
                elif declared_type == "float" and isinstance(value, int):
                    casted_val = float(value)
                else:
                    casted_val = value
                self.variables[name] = casted_val
            except (ValueError, TypeError):
                self.errorWrongType(type(value).__name__, declared_type, name, ctx)

        elif isinstance(target_ctx, PhysicsParser.AttrTargetContext):
            obj, attr, index = self.visit(target_ctx)
            if index is not None:
                getattr(obj, attr)[index] = value
            else:
                setattr(obj, attr, value)

        return None

    # ————————————————————————————————————————————————————————————————
    # Deklaracje funkcji / praw
    # ————————————————————————————————————————————————————————————————

    def visitFuncDecl(self, ctx):
        name      = ctx.ID().getText()
        ret_type  = ctx.returnType().getText() if ctx.returnType() else "void"   # ◆
        # 1. zbierz (nazwa, typ)
        params = []
        if ctx.paramList():
            for p in ctx.paramList().param():
                p_type = p.type_().getText()
                p_name = p.ID().getText()
                params.append((p_name, p_type))

        # 2. powtórzone nazwy?
        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self._error(ctx, f"Duplicate parameter name '{dup}' in function '{name}'")

        # 3. redeklaracja funkcji?
        if name in self.functions and self.functions[name].get("defined", False):
            self._error(ctx, f"Redeclaration of function '{name}'")

        # 4. zapisz metadane
        self.functions[name] = {
        "ret"   : ret_type,          # ◆  NOWE POLE
        "params": params,
        "expr"  : ctx.expr()  if ctx.expr()  else None,
        "block" : ctx.block() if ctx.block() else None,
        "defined": True,
    }
        return None


    # ─────────────────────────────────────────────────────────────
    #  visitLawDecl
    # ─────────────────────────────────────────────────────────────
    def visitLawDecl(self, ctx):
        name = ctx.ID().getText()

        params = []
        if ctx.paramList():
            for p in ctx.paramList().param():
                p_type = p.type_().getText()
                p_name = p.ID().getText()
                params.append((p_name, p_type))

        names_only = [n for n, _ in params]
        if len(names_only) != len(set(names_only)):
            dup = next(n for n in names_only if names_only.count(n) > 1)
            self._error(ctx, f"Duplicate parameter name '{dup}' in law '{name}'")

        if name in self.functions and self.functions[name].get("defined", False):
            self._error(ctx, f"Redeclaration of law '{name}'")

        self.functions[name] = {
            "params": params,                           # ← lista krotek
            "expr"  : None,
            "block" : ctx.block(),
            "defined": True,
        }
        return None

    # ————————————————————————————————————————————————————————————————
    # Prawa przypisywane do systemów / cząstek
    # ————————————————————————————————————————————————————————————————

    def visitLawAssignStmt(self, ctx):
        target_name = ctx.dottedID().getText()
        law_name = ctx.ID().getText()

        if law_name not in self.functions:
            self._error(ctx, f"Law '{law_name}' not defined")
        law_meta = self.functions[law_name]

        fn = self._wrap_fn(law_meta)
        target_obj = self.variables.get(target_name)

        if isinstance(target_obj, System):
            target_obj.register_law(Law(fn=fn, scope=target_name, target="particle"))
        elif isinstance(target_obj, Particle):
            self.global_laws.append(Law(fn=fn, scope=target_name, target="particle"))
        else:
            self._error(ctx, f"Cannot assign law to object of type {type(target_obj)}")
        return None

    # ————————————————————————————————————————————————————————————————
    # Deklaracja systemu (zagnieżdżone systemy wspierane)
    # ————————————————————————————————————————————————————————————————

    def visitSystemDecl(self, ctx):
        name = ctx.ID().getText()

        if name in self.variables:
            self._error(ctx, f"Redeclaration of variable '{name}'")

        if name in self.symbol_table and self.symbol_table[name] != "system":
            self._error(
                ctx,
                f"Redeclaration of variable '{name}' as system "
                f"(was {self.symbol_table[name]})"
            )

        self.symbol_table[name] = "system"

        system = System(name)
        self.variables[name] = system


        prev_active = self.current_system
        self.current_system = system

        self.visit(ctx.block())

        self.current_system = prev_active
        return None

    # ————————————————————————————————————————————————————————————————
    # Pomocnicze – wrapped function używana w prawach
    # ————————————————————————————————————————————————————————————————

    def _wrap_fn(self, meta):
        def fn(obj, system, dt):
            # zablokuj rekurencję field->function
            saved_current = self.variables.get("$CURRENT_FN")
            if saved_current == meta:
                raise Exception("Illegal recursion: field->function cannot call itself")
            self.variables["$CURRENT_FN"] = meta

            # ─── przygotuj lokalny kontekst ───
            saved_vars = self.variables
            self.variables = saved_vars.copy()

            # META['params'] to lista [(nazwa, typ), …]
            if meta["params"]:
                param_name = meta["params"][0][0]   # <-- tylko nazwa!
                self.variables[param_name] = obj

            # wykonaj blok prawa
            self.visit(meta["block"])

            # przywróć stare zmienne
            self.variables = saved_vars
            self.variables["$CURRENT_FN"] = saved_current
        return fn



    # ————————————————————————————————————————————————————————————————
    # Wywołania funkcji (w tym rekurencyjne)
    # ————————————————————————————————————————————————————————————————

    def _call(self, name: str, args: list, call_ctx):
        # ───────────────────────────────────────────────
        # 0.  czy funkcja istnieje?
        # ───────────────────────────────────────────────
        if name not in self.functions:
            self._error(call_ctx, f"Unknown function '{name}'")

        sig              = self.functions[name]
        expected_params  = sig["params"]        # [(nazwa, typ), …]
        ret_type         = sig.get("ret", "void")   # ◀─ NOWE

        # Użyjemy też przy sprawdzaniu wyników
        TYPE_MAP = {
            "int"      : int,
            "float"    : float,
            "bool"     : bool,
            "particle" : Particle,
            "field"    : Field,
            "system"   : System,
            "void"     : type(None)
        }

        # ───────────────────────────────────────────────
        # 1.  liczba argumentów
        # ───────────────────────────────────────────────
        if len(args) != len(expected_params):
            self._error(call_ctx,
                f"Function '{name}' expects {len(expected_params)} arguments, got {len(args)}")

        # ───────────────────────────────────────────────
        # 2.  typy argumentów
        # ───────────────────────────────────────────────
        args_casted: list[Any] = []                          # ❶
        for (p_name, p_type), arg in zip(expected_params, args):

            exp_cls = TYPE_MAP[p_type]

            # ─── ❶ blokada bool-a dla parametrów liczbowych ───
            if p_type in ("int", "float") and isinstance(arg, bool):
                self._error(
                    call_ctx,
                    f"In function '{name}' parameter '{p_name}' expects {p_type}, "
                    "got bool"
                )

            ok = isinstance(arg, exp_cls)

            # auto-rzutowanie  int → float  (ale NIE bool!)
            if (not ok
                and p_type == "float"
                and isinstance(arg, int)
                and not isinstance(arg, bool)):     # <── zapobiega bool→float
                arg = float(arg)
                ok  = True

            if not ok:
                self._error(
                    call_ctx,
                    f"In function '{name}' parameter '{p_name}' expects {p_type}, "
                    f"got {type(arg).__name__}"
                )

            args_casted.append(arg)  

        # ───────────────────────────────────────────────
        # 3.  rekord aktywacji
        # ───────────────────────────────────────────────
        saved_vars = self.variables
        self.variables = saved_vars.copy()
        saved_functions = self.functions
        self.functions = saved_functions.copy()

        for (p_name, p_type), arg in zip(expected_params, args_casted):   # ➍
            self.variables[p_name]    = arg
            self.symbol_table[p_name] = p_type

        # ───────────────────────────────────────────────
        # 4.  wykonaj ciało
        # ───────────────────────────────────────────────
        self.in_function = True
        self.return_value = None                   # <-- reset

        try:
            if sig["expr"]:                        # forma „=> expr”
                value = self.visit(sig["expr"])    # ①
            else:                                  # blok z 'return'-ami
                self.visit(sig["block"])
                value = self.return_value
        finally:
            self.variables = saved_vars
            self.functions = saved_functions
            self.in_function = False
            self.return_value = None

        # ───────────────────────────────────────────────
        # 5.  WALIDACJA  wyniku  (typ + obowiązek)
        # ───────────────────────────────────────────────
        if ret_type == "void":
            if value is not None:
                self._error(call_ctx,
                    f"Function '{name}' declared void but returns a value")
            return None                     # wszystko OK

        # Funkcja z typem zwracanym MUSI zwracać wartość
        if value is None:
            self._error(call_ctx,
                f"Function '{name}' must return {ret_type} but reached end without return")

        # auto-rzutowanie int → float przy zwracaniu
        if ret_type == "float" and isinstance(value, int):
            value = float(value)

        if not isinstance(value, TYPE_MAP[ret_type]):
            self._error(call_ctx,
                f"Function '{name}' should return {ret_type}, got {type(value).__name__}")

        return value

    # ————————————————————————————————————————————————————————————————
    # Bloki, instrukcje sterujące, pętle
    # ————————————————————————————————————————————————————————————————

    def visitBlock(self, ctx):
        for st in ctx.statement():
            self.visit(st)
            if self.in_function and self.return_value is not None:
                break
        return None

    def visitIfStmt(self, ctx):
        cond = self.visit(ctx.expr(0))
        if cond:
            self.visit(ctx.block(0))
            return None

        n_conds = len(ctx.expr())
        n_blocks = len(ctx.block())
        for i in range(1, n_conds):
            if self.visit(ctx.expr(i)):
                self.visit(ctx.block(i))
                return None
        if n_blocks > n_conds:
            self.visit(ctx.block(n_blocks - 1))
        return None

    #TODO: po co ziększa się czas
    def visitWhileStmt(self, ctx):
        guard_counter = 0  # zabezpiecz kontra nieskończonej pętli
        while self.visit(ctx.expr()):
            self.visit(ctx.block())
            # czemu czas się zwiększa??
            self.variables["$TIME"] += 1
            guard_counter += 1
            if guard_counter > 10**6:
                self._error(ctx, "Potential infinite while‑loop detected – breaking execution")
        return None

    def visitForStmt(self, ctx):
        var_name  = ctx.ID().getText()
        decl_type = ctx.type_().getText() if ctx.type_() else None   # ← NEW
        start_val = self.visit(ctx.expr(0))
        end_val   = self.visit(ctx.expr(1))
        step_val  = self.visit(ctx.expr(2))

        if step_val == 0:
            self._error(ctx, "For-loop step cannot be zero")

        # ─────────────────────────────────────────────────────────
        # 1) Jeśli typ podany w nagłówku → to nowa deklaracja
        #    (dozwolone tylko int/float, brak redeklaracji)
        # ─────────────────────────────────────────────────────────
        if decl_type:
            if decl_type not in ("int", "float"):
                self._error(ctx,
                    f"For-loop variable '{var_name}' must be int or float, not {decl_type}")
            if var_name in self.symbol_table:
                self._error(ctx,
                    f"Redeclaration of variable '{var_name}' in for-loop header")
            self.symbol_table[var_name] = decl_type
            # możesz dać wartość startową, ale nie jest to konieczne
            self.variables[var_name] = start_val if decl_type == "float" else int(start_val)

        # ─────────────────────────────────────────────────────────
        # 2) Brak typu w nagłówku → zmienna MUSI istnieć
        #    i być int/float
        # ─────────────────────────────────────────────────────────
        else:
            if var_name not in self.symbol_table:
                self._error(ctx,
                    f"Variable '{var_name}' used in for-loop was not declared earlier")
            declared_type = self.symbol_table[var_name]
            if declared_type not in ("int", "float"):
                self._error(ctx,
                    f"For-loop variable '{var_name}' must be int or float, not {declared_type}")

        # —— normalna pętla ——
        #TODO: po co i
        # TODO: po co ziększa się czas
        i   = start_val
        cmp = (lambda a, b: a <= b) if step_val >= 0 else (lambda a, b: a >= b)
        while cmp(i, end_val):
            self.variables[var_name] = i
            self.visit(ctx.block())
            i = self.variables[var_name]
            # czemu czas się zwiększa??
            self.variables["$TIME"] += 1
            i += step_val

    #TODO: po co ziększa się czas
    def visitForeachStmt(self, ctx):
        var_name = ctx.ID(0).getText()
        system_name = ctx.ID(1).getText()

        system_obj = self.variables.get(system_name)
        if not isinstance(system_obj, System):
            self._error(ctx, f"'{system_name}' is not a system in foreach loop")

        for _, particle in system_obj.particles.items():
            self.variables[var_name] = particle
            self.symbol_table[var_name] = True
            self.visit(ctx.block())
            # czemu czas się zwiększa??
            self.variables["$TIME"] += 1
        return None

    # ————————————————————————————————————————————————————————————————
    # Return & print
    # ————————————————————————————————————————————————————————————————

    def visitReturnStmt(self, ctx):
        self.return_value = self.visit(ctx.expr())
        return self.return_value

    def visitPrintStmt(self, ctx):
        val = self.visit(ctx.expr())
        if val is None:
            self._error(ctx, "Invalid use of void expression")
        print(val)
        return None

    # ————————————————————————————————————————————————————————————————
    # Ekspresje – logika i arytmetyka z kontrolą typów
    # ————————————————————————————————————————————————————————————————

    def visitExpr(self, ctx):
        return self.visit(ctx.logicOr())

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

    def visitCompare(self, ctx):
        return self.visit(ctx.addSub())

    def visitAddSub(self, ctx):
        res = self.visit(ctx.mulDiv(0))
        for i in range(1, len(ctx.mulDiv())):
            op = ctx.getChild(2 * i - 1).getText()
            val = self.visit(ctx.mulDiv(i))

            if isinstance(res, bool) or isinstance(val, bool):
                self.errorWrongAction(op, (type(res), type(val)), res, val, ctx)

            res = res + val if op == "+" else res - val
        return res

    def visitMulDiv(self, ctx):
        res = self.visit(ctx.power(0))
        for i in range(1, len(ctx.power())):
            op = ctx.getChild(2 * i - 1).getText()
            val = self.visit(ctx.power(i))

            if isinstance(res, bool) or isinstance(val, bool):
                self.errorWrongAction(op, (type(res), type(val)), res, val, ctx)

            if op == "*":
                res *= val
            else:
                if val == 0:
                    self._error(ctx, "Division by zero")
                res = res // val if op == "//" else res / val
        return res

    def visitPower(self, ctx):
        res = self.visit(ctx.unary(0))
        for i in range(1, len(ctx.unary())):
            val = self.visit(ctx.unary(i))
            if isinstance(res, bool) or isinstance(val, bool):
                self.errorWrongAction("^", (type(res), type(val)), res, val, ctx)
            res **= val
        return res

    def visitUnary(self, ctx):
        # Operator "?" – sprawdzanie obecności atrybutu
        if ctx.getChildCount() == 3 and ctx.getChild(1).getText() == '?':
            obj_name = ctx.dottedID().getText()
            attr_name = ctx.ID().getText()
            obj = self.variables[obj_name]
            return hasattr(obj, attr_name)

        # Unary plus/minus, not
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            val = self.visit(ctx.unary())
            if (isinstance(val, bool) and op!= "Not") or (not isinstance(val, bool) and op== "Not"):
                self._error(ctx,f"Operator {op} cannot be used on variable of type {type(val)}")

            return {"Not": lambda x: not x, "-": lambda x: -x, "+": lambda x: +x}[op](val)

        return self.visit(ctx.atom())

    def visitVector(self, ctx):
        return [self.visit(e) for e in ctx.expr()]

    # ————————————————————————————————————————————————————————————————
    # Atom – identyfikatory, literały, wywołania
    # ————————————————————————————————————————————————————————————————

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
        if text == "True":
            return True
        if text == "False":
            return False

        # Wywołanie funkcji

        if "(" in text:
            # a) zwykła nazwa funkcji
            if "->" not in text:
                func_name = ctx.dottedID().getText()
                args      = [self.visit(a) for a in ctx.argList().expr()] if ctx.argList() else []
                return self._call(func_name, args, ctx)

            # b) wywołanie atrybutu-funkcji:  g->function(...)
            obj_part, rest = text.split("->", 1)         # 'g'  , 'function(…'
            attr_name      = rest.split("(", 1)[0]       # 'function'
            obj            = self.variables[obj_part]

            fn = getattr(obj, attr_name)
            if not callable(fn):
                self._error(ctx, f"Attribute '{attr_name}' of '{obj_part}' is not callable")

            args = [self.visit(a) for a in ctx.argList().expr()] if ctx.argList() else []
            return fn(*args)


        # Dostęp do atrybutu / elementu
        if "->" in text:
            obj_name, rest = text.split("->", 1)
            obj = self.variables[obj_name]
            if "[" in rest:
                attr, idx_txt = rest[:-1].split("[")
                return getattr(obj, attr)[int(idx_txt)]
            return getattr(obj, rest)

        # Zmienna zwykła
        # Zmienna zwykła
        if text in self.symbol_table:
            if text not in self.variables or self.variables[text] is None:
                self._error(ctx, f"Use of uninitialized variable '{text}'")
            return self.variables[text]

        # ─── te dwa bloki muszą być w tym samym „poziomie” co powyższy ───
        # Specjalne zmienne z prefiksem $
        if text.startswith("$") and text in self.variables:
            return self.variables[text]

        # nazwa *zdefiniowanej* funkcji bez nawiasów → zwracamy callable
        if text in self.functions:
            def free_fn(*args):
                return self._call(text, list(args), ctx)   # ctx zdefiniowane wyżej
            return free_fn
        # ──────────────────────────────────────────────────────────────────

        self._error(ctx, f"Use of undeclared variable '{text}'")



    # ————————————————————————————————————————————————————————————————
    # Przypisania do atrybutów (skrócona forma)
    # ————————————————————————————————————————————————————————————————

    def visitAttrTarget(self, ctx):
        obj_name = ctx.dottedID().getText()
        attr_name = ctx.ID().getText()
        obj = self.variables[obj_name]
        index = self.visit(ctx.expr()) if ctx.expr() else None
        return obj, attr_name, index

    def visitAttrAssignStmt(self, ctx):
        obj_name = ctx.dottedID().getText()
        attr_name = ctx.ID().getText()
        obj = self.variables[obj_name]
        value = self.visit(ctx.expr()) if ctx.expr() else 0.0
        setattr(obj, attr_name, value)
        return None

    # ————————————————————————————————————————————————————————————————
    # Scope - parenty
    # ————————————————————————————————————————————————————————————————

    def visitParentAccess(self, ctx):
        var_name = ctx.ID().getText()
        parent_scope = self.current_scope.parent
        if parent_scope is None:
            raise RuntimeError(f"No parent scope for 'parent::{var_name}'")
        if var_name not in parent_scope.symbols:
            raise RuntimeError(f"'{var_name}' not found in parent scope")
        return parent_scope.symbols[var_name]

    # ————————————————————————————————————————————————————————————————
    # Specjalna funkcja run – symulacje w czasie
    # ————————————————————————————————————————————————————————————————

    def visitCall(self, ctx):
        func_name = ctx.dottedID().getText()
        args = [self.visit(a) for a in ctx.argList().expr()] if ctx.argList() else []

        if func_name == "run":
            if len(args) not in (2, 3):
                self._error(ctx, "Function 'run' expects 2 or 3 arguments")

            obj, steps, *rest = args
            dt = float(rest[0]) if rest else 1.0
            steps = int(steps)

            if isinstance(obj, System):
                for _ in range(steps):
                    obj.laws += self.global_laws
                    obj.step(dt)
                    self.variables["$TIME"] = obj.time
                return None

            if isinstance(obj, Particle):
                # Znajdź nazwę zmiennej tej cząstki.
                name = next((vn for vn, vo in self.variables.items() if vo is obj), None)
                if name is None:
                    self._error(ctx, "Particle reference not found in variables table")

                for _ in range(steps):
                    for law in self.global_laws:
                        if law.applies(name, obj):
                            law.fn(obj, None, dt)
                    for i in range(3):
                        obj.position[i] += obj.velocity[i] * dt
                    self.variables["$TIME"] += dt
                return None

            self._error(ctx, "First argument of 'run' must be system or particle")

        # Normalne wywołanie funkcji
        return self._call(func_name, args, ctx)

    # ————————————————————————————————————————————————————————————————
    # Particle
    # ————————————————————————————————————————————————————————————————

    def visitParticleDecl(self, ctx):
        name = ctx.ID().getText()

        if name in self.variables:
            self._error(ctx, f"Variable '{name}' already declared")

        particle = Particle()
        self.variables[name] = particle

        self.current_particle = name
        for stmt in ctx.block().statement():
            self.visit(stmt)
        self.current_particle = None

    def visitSystemDecl(self, ctx):
        name = ctx.ID().getText()

        if name in self.variables:
            self._error(ctx, f"Variable '{name}' already declared")

        system = System(name)
        self.variables[name] = system

        self.current_system = name

        for stmt in ctx.block().statement():
            self.visit(stmt)

        self.current_system = None



