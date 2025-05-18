# Generated from Physics.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .PhysicsParser import PhysicsParser
else:
    from PhysicsParser import PhysicsParser

# This class defines a complete generic visitor for a parse tree produced by PhysicsParser.

class PhysicsVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PhysicsParser#prog.
    def visitProg(self, ctx:PhysicsParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#statement.
    def visitStatement(self, ctx:PhysicsParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#declStmt.
    def visitDeclStmt(self, ctx:PhysicsParser.DeclStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#assignStmt.
    def visitAssignStmt(self, ctx:PhysicsParser.AssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#varTarget.
    def visitVarTarget(self, ctx:PhysicsParser.VarTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#attrTarget.
    def visitAttrTarget(self, ctx:PhysicsParser.AttrTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#lawDecl.
    def visitLawDecl(self, ctx:PhysicsParser.LawDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#lawAssignStmt.
    def visitLawAssignStmt(self, ctx:PhysicsParser.LawAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#attrAssignStmt.
    def visitAttrAssignStmt(self, ctx:PhysicsParser.AttrAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#call.
    def visitCall(self, ctx:PhysicsParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#systemDecl.
    def visitSystemDecl(self, ctx:PhysicsParser.SystemDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#funcDecl.
    def visitFuncDecl(self, ctx:PhysicsParser.FuncDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#paramList.
    def visitParamList(self, ctx:PhysicsParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#param.
    def visitParam(self, ctx:PhysicsParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#controlStmt.
    def visitControlStmt(self, ctx:PhysicsParser.ControlStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#ifStmt.
    def visitIfStmt(self, ctx:PhysicsParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#whileStmt.
    def visitWhileStmt(self, ctx:PhysicsParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#forStmt.
    def visitForStmt(self, ctx:PhysicsParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#foreachStmt.
    def visitForeachStmt(self, ctx:PhysicsParser.ForeachStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#printStmt.
    def visitPrintStmt(self, ctx:PhysicsParser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#returnStmt.
    def visitReturnStmt(self, ctx:PhysicsParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#emptyLine.
    def visitEmptyLine(self, ctx:PhysicsParser.EmptyLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#expr.
    def visitExpr(self, ctx:PhysicsParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#logicOr.
    def visitLogicOr(self, ctx:PhysicsParser.LogicOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#logicAnd.
    def visitLogicAnd(self, ctx:PhysicsParser.LogicAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#equality.
    def visitEquality(self, ctx:PhysicsParser.EqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#compare.
    def visitCompare(self, ctx:PhysicsParser.CompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#addSub.
    def visitAddSub(self, ctx:PhysicsParser.AddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#mulDiv.
    def visitMulDiv(self, ctx:PhysicsParser.MulDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#power.
    def visitPower(self, ctx:PhysicsParser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#unary.
    def visitUnary(self, ctx:PhysicsParser.UnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#vector.
    def visitVector(self, ctx:PhysicsParser.VectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#atom.
    def visitAtom(self, ctx:PhysicsParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#argList.
    def visitArgList(self, ctx:PhysicsParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#type.
    def visitType(self, ctx:PhysicsParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#returnType.
    def visitReturnType(self, ctx:PhysicsParser.ReturnTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#block.
    def visitBlock(self, ctx:PhysicsParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhysicsParser#dottedID.
    def visitDottedID(self, ctx:PhysicsParser.DottedIDContext):
        return self.visitChildren(ctx)



del PhysicsParser