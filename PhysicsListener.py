# Generated from Physics.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .PhysicsParser import PhysicsParser
else:
    from PhysicsParser import PhysicsParser

# This class defines a complete listener for a parse tree produced by PhysicsParser.
class PhysicsListener(ParseTreeListener):

    # Enter a parse tree produced by PhysicsParser#prog.
    def enterProg(self, ctx:PhysicsParser.ProgContext):
        pass

    # Exit a parse tree produced by PhysicsParser#prog.
    def exitProg(self, ctx:PhysicsParser.ProgContext):
        pass


    # Enter a parse tree produced by PhysicsParser#statement.
    def enterStatement(self, ctx:PhysicsParser.StatementContext):
        pass

    # Exit a parse tree produced by PhysicsParser#statement.
    def exitStatement(self, ctx:PhysicsParser.StatementContext):
        pass


    # Enter a parse tree produced by PhysicsParser#declStmt.
    def enterDeclStmt(self, ctx:PhysicsParser.DeclStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#declStmt.
    def exitDeclStmt(self, ctx:PhysicsParser.DeclStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#assignStmt.
    def enterAssignStmt(self, ctx:PhysicsParser.AssignStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#assignStmt.
    def exitAssignStmt(self, ctx:PhysicsParser.AssignStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#target.
    def enterTarget(self, ctx:PhysicsParser.TargetContext):
        pass

    # Exit a parse tree produced by PhysicsParser#target.
    def exitTarget(self, ctx:PhysicsParser.TargetContext):
        pass


    # Enter a parse tree produced by PhysicsParser#lawDecl.
    def enterLawDecl(self, ctx:PhysicsParser.LawDeclContext):
        pass

    # Exit a parse tree produced by PhysicsParser#lawDecl.
    def exitLawDecl(self, ctx:PhysicsParser.LawDeclContext):
        pass


    # Enter a parse tree produced by PhysicsParser#funcDecl.
    def enterFuncDecl(self, ctx:PhysicsParser.FuncDeclContext):
        pass

    # Exit a parse tree produced by PhysicsParser#funcDecl.
    def exitFuncDecl(self, ctx:PhysicsParser.FuncDeclContext):
        pass


    # Enter a parse tree produced by PhysicsParser#paramList.
    def enterParamList(self, ctx:PhysicsParser.ParamListContext):
        pass

    # Exit a parse tree produced by PhysicsParser#paramList.
    def exitParamList(self, ctx:PhysicsParser.ParamListContext):
        pass


    # Enter a parse tree produced by PhysicsParser#param.
    def enterParam(self, ctx:PhysicsParser.ParamContext):
        pass

    # Exit a parse tree produced by PhysicsParser#param.
    def exitParam(self, ctx:PhysicsParser.ParamContext):
        pass


    # Enter a parse tree produced by PhysicsParser#type.
    def enterType(self, ctx:PhysicsParser.TypeContext):
        pass

    # Exit a parse tree produced by PhysicsParser#type.
    def exitType(self, ctx:PhysicsParser.TypeContext):
        pass


    # Enter a parse tree produced by PhysicsParser#controlStmt.
    def enterControlStmt(self, ctx:PhysicsParser.ControlStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#controlStmt.
    def exitControlStmt(self, ctx:PhysicsParser.ControlStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#ifStmt.
    def enterIfStmt(self, ctx:PhysicsParser.IfStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#ifStmt.
    def exitIfStmt(self, ctx:PhysicsParser.IfStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#whileStmt.
    def enterWhileStmt(self, ctx:PhysicsParser.WhileStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#whileStmt.
    def exitWhileStmt(self, ctx:PhysicsParser.WhileStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#forStmt.
    def enterForStmt(self, ctx:PhysicsParser.ForStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#forStmt.
    def exitForStmt(self, ctx:PhysicsParser.ForStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#foreachStmt.
    def enterForeachStmt(self, ctx:PhysicsParser.ForeachStmtContext):
        pass

    # Exit a parse tree produced by PhysicsParser#foreachStmt.
    def exitForeachStmt(self, ctx:PhysicsParser.ForeachStmtContext):
        pass


    # Enter a parse tree produced by PhysicsParser#block.
    def enterBlock(self, ctx:PhysicsParser.BlockContext):
        pass

    # Exit a parse tree produced by PhysicsParser#block.
    def exitBlock(self, ctx:PhysicsParser.BlockContext):
        pass


    # Enter a parse tree produced by PhysicsParser#expr.
    def enterExpr(self, ctx:PhysicsParser.ExprContext):
        pass

    # Exit a parse tree produced by PhysicsParser#expr.
    def exitExpr(self, ctx:PhysicsParser.ExprContext):
        pass


    # Enter a parse tree produced by PhysicsParser#atom.
    def enterAtom(self, ctx:PhysicsParser.AtomContext):
        pass

    # Exit a parse tree produced by PhysicsParser#atom.
    def exitAtom(self, ctx:PhysicsParser.AtomContext):
        pass


    # Enter a parse tree produced by PhysicsParser#argList.
    def enterArgList(self, ctx:PhysicsParser.ArgListContext):
        pass

    # Exit a parse tree produced by PhysicsParser#argList.
    def exitArgList(self, ctx:PhysicsParser.ArgListContext):
        pass


    # Enter a parse tree produced by PhysicsParser#particleType.
    def enterParticleType(self, ctx:PhysicsParser.ParticleTypeContext):
        pass

    # Exit a parse tree produced by PhysicsParser#particleType.
    def exitParticleType(self, ctx:PhysicsParser.ParticleTypeContext):
        pass



del PhysicsParser