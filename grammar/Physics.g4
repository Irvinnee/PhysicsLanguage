grammar Physics;

tokens { INDENT, DEDENT }

@lexer::header{
from antlr_denter.DenterHelper import DenterHelper
from PhysicsParser import PhysicsParser
}
@lexer::members {
class MyCoolDenter(DenterHelper):
    def __init__(self, lexer, nl_token, indent_token, dedent_token, ignore_eof):
        super().__init__(nl_token, indent_token, dedent_token, ignore_eof)
        self.lexer: PhysicsLexer = lexer

    def pull_token(self):
        return super(PhysicsLexer, self.lexer).nextToken()

denter = None

def nextToken(self):
    if not self.denter:
        self.denter = self.MyCoolDenter(self, self.NL, PhysicsParser.INDENT, PhysicsParser.DEDENT, False)
    return self.denter.next_token()

}


prog        : statement* EOF ;

statement
    : declStmt
    | assignStmt
    | systemAddStmt
    | callStmt
    | lawDecl
    | systemDecl
    | lawAssignStmt 
    | funcDecl
    | controlStmt
    | printStmt
    | returnStmt
    | emptyLine
    ;

declStmt    : type ID ('=' expr)? NL ;
assignStmt  : target '=' expr NL ;

target
    : dottedID                                   #varTarget
    | dottedID '->' ID ('[' expr ']')?           #attrTarget
    ;


lawDecl     : 'law' ID '(' paramList? ')' ':'
               block;

lawAssignStmt : '<' dottedID '&' ID '>' NL ;
systemAddStmt
    : dottedID '<-' ID NL
    ;
callStmt
    : dottedID '(' argList? ')' NL      #call
    ;

systemDecl
    : 'system' ID ':' block
    ;

funcDecl
    : 'func' ID '(' paramList? ')' (
          '=>' expr NL
        | ':' block
      ) ;

paramList   : param (',' param)* ;
param       : type ID ;

controlStmt : ifStmt | whileStmt | forStmt | foreachStmt ;

ifStmt
    : 'if' '(' expr ')' ('=>' expr NL | ':' block)
      ( 'elsif' '(' expr ')' ('=>' expr NL | ':' block) )*
      ( 'else' ('=>' expr NL | ':' block) )? ;

whileStmt   : 'while' '(' expr ')' ':' block ;

forStmt
    : 'for' type? ID '(' expr ',' expr ',' expr ')' ':'
        block ;

foreachStmt
    : 'foreach' type? ID '(' ID ')' ':'
     block;

printStmt   : 'print' '(' expr ')' NL ;
returnStmt  : '=>' expr NL ;
emptyLine   : NL ;

expr        : logicOr ;

logicOr     : logicAnd ( 'Or'  logicAnd )* ;
logicAnd    : equality ( 'And' equality )* ;
equality    : compare  ( ('=='|'!='|'>='|'<='|'>'|'<') compare )* ;
compare     : addSub ;
addSub      : mulDiv  ( ('+'|'-') mulDiv)* ;
mulDiv      : power   ( ('*'|'/') power)* ;
power       : unary   ( '^' unary )* ;

unary
    : dottedID '?' ID
    | ('Not'|'-'|'+') unary
    | atom
    ;

vector      : '[' expr (',' expr)* ']' ;

atom
    : INT
    | FLOAT
    | (dottedID ('->' ID ('[' expr ']')?)?) ('(' argList? ')')?
    | vector
    | '(' expr ')' ;

argList     : expr (',' expr)* ;

type        : 'particle' | 'field' | 'system'
            | 'float' | 'int' | 'bool' ;

block           : INDENT statement+ DEDENT ;

ID : ('$'? [\p{L}_]) [\p{L}\p{N}_]* ;



INT         : [0-9]+ ;
FLOAT       : [0-9]+ '.' [0-9]* ;

COMMENT         : '%' ~[\r\n]* -> skip ;
WS              : [ \t\f]+ -> skip;

NL: ('\r'? '\n' ' '*);


dottedID    : ID ('.' ID)* ;