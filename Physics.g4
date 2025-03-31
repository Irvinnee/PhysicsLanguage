grammar Physics;

prog         : statement* EOF ;
statement       : declStmt | assignStmt | lawDecl | funcDecl | controlStmt ;
declStmt        : ('Particle' | 'Field' | 'system') ID ;
assignStmt      : target ARROW? expr ;
target          : ID ('->' ID ( '[' INT ']' )? | '<-' ID ) ;
lawDecl         : 'law' ID '(' paramList? ')' block ;
funcDecl        : 'func' ID '(' paramList? ')' ( '=>' expr | block ) ;
paramList       : param (',' param)* ;
param           : type? ID ;
type            : 'particle' | 'field' | 'float' | 'int' ;
controlStmt     : ifStmt | whileStmt | forStmt | foreachStmt ;
ifStmt          : 'if' '(' expr ')' block ( 'elsif' '(' expr ')' block )* ( 'else' block )? ;
whileStmt       : 'while' '(' expr ')' block ;
forStmt         : 'for' type? ID '(' expr ',' expr ',' expr ')' block ;
foreachStmt     : 'foreach' type? ID '(' ID ')' block ;
block           : '{'? statement* '}'? ;
expr            : atom (('+'|'-'|'*'|'/'|'^') expr)? ;
atom            : INT | FLOAT | ID ( '(' argList? ')' )? | target | '[' expr (',' expr)* ']' ;
argList         : expr (',' expr)* ;

ARROW           : '->' | '<-' ;
ID              : [a-zA-Z_]+[a-zA-Z0-9]* ;
INT             : [0-9]+ ;
FLOAT           : [0-9]+'.'[0-9]* ;
WS              : [ \t\r\n]+ -> skip ;
COMMENT         : '%' ~[\r\n]* -> skip ;