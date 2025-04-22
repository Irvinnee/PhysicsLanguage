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


prog            : statement* EOF ;
statement       : declStmt | assignStmt | lawDecl | funcDecl | controlStmt | NL;
declStmt        : particleType ID ('=' expr)? NL;
assignStmt      : target ARROW? expr NL;
target          : ID ('->' ID ( '[' INT ']' )? | '<-' ID ) ;
lawDecl         : 'law' ID '(' paramList? ')' block ;
funcDecl        : 'func' ID '(' paramList? ')' ( '=>' expr | block ) ;
paramList       : param (',' param)* ;
param           : type ID ;
type            : 'particle' | 'field' | 'float' | 'int' | 'bool' ;
controlStmt     : ifStmt | whileStmt | forStmt | foreachStmt ;
ifStmt          : 'if' '(' expr ')' block ( 'elsif' '(' expr ')' block )* ( 'else' block )? ;
whileStmt       : 'while' '(' expr ')' block ;
forStmt         : 'for' type? ID '(' expr ',' expr ',' expr '):'  block ;
foreachStmt     : 'foreach' type? ID '(' ID ')' block ;
block           : INDENT statement+ DEDENT ;
expr            : atom (('+'|'-'|'*'|'/'|'^'|'Not'|'And'|'Or'|'=='|'>='|'<='|'>'|'<') expr)? ;
atom            : INT | FLOAT | ID ( '(' argList? ')' )? | target | '[' expr (',' expr)* ']' ;
argList         : expr (',' expr)* ;

NL: ('\r'? '\n' ' '*);
ARROW           : '->' | '<-' ;
ID              : [a-zA-Z_]+[a-zA-Z0-9]* ;
INT             : [0-9]+ ;
FLOAT           : [0-9]+'.'[0-9]* ;
WS              : [ \t\f]+                             -> channel(HIDDEN);
COMMENT         : '%' ~[\r\n]* -> skip ;

//NEWLINE : '\n' -> skip ;

particleType    : 'Particle' | 'Field' | 'System' | 'int' | 'float' | 'bool' ;