grammar Physics;

// tokeny odpowiadające za wcięcia w kodzie
tokens { INDENT, DEDENT }

// klasy obsługujące wcięcia w kodzie
// korzystają z bibliioteki antlr-denter
@lexer::header{
from antlr_denter.DenterHelper import DenterHelper
from grammar.PhysicsParser import PhysicsParser
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

// ogólne wyrażenia w gramatyce
statement
    : declStmt              //deklaracja zmiennej
    | assignStmt            //przypisanie zmiennej
    | attrAssignStmt        //przypisanie atrybutu do cząstki
    | callStmt              //wywołanie funkcji
    | lawDecl               //deklaracja prawa
    | particleDecl          //deklaracja cząsteczki
    | systemDecl            //deklaracja systemu
    | lawAssignStmt         //przypisanie prawa do cząsteczki
    | funcDecl              //deklaracja funkcji
    | controlStmt           //wyrażenie kontrolne odpowiadające za pętle, wyrażenia warunkowe itp.
    | printStmt             //funkcja print
    | returnStmt            //zwracanie wartości
    | emptyLine             //pusta linia
    ;

//deklaracja
declStmt    : type ID ('=' expr)? NL ;
//przyporządkowanie
assignStmt  : target '=' expr NL ;

//"cel" przyporządkowania
target
    : dottedID                                   #varTarget
    | dottedID '->' ID ('[' expr ']')?           #attrTarget
    ;

//deklaracja prawa
lawDecl     : 'law' ID '(' paramList? ')' ':'
               block;

//deklaracja cząsteczki
particleDecl
    : 'particle' ID ':' block
    ;

//przyporządkowanie prawa
lawAssignStmt : '<' argList '&' ID '>' NL ;

//przyporządkowanie argumentu
attrAssignStmt
    : dottedID '<-' ID ('=' expr)? NL
    ;

//wywołanie funkcji
callStmt
    : dottedID '(' argList? ')' NL      #call
    ;

//deklaracja systemu
systemDecl
    : 'system' ID ':' block
    ;

//deklaracja funkcji
funcDecl
    : returnType? 'func' ID '(' paramList? ')'
        ( '=>' expr NL
        | ':' block
        )
    ;

paramList   : param (',' param)* ;  //lista parametrów
param       : type ID ;             //pojedynczy parametr

//wyrażenia kontrolne
controlStmt : ifStmt | whileStmt | forStmt | foreachStmt ;

//wyrażenia warunkowe
ifStmt
    : 'if' '(' expr ')' ('=>' expr NL | ':' block)
      ( 'elsif' '(' expr ')' ('=>' expr NL | ':' block) )*
      ( 'else' ('=>' expr NL | ':' block) )? ;

//pętle
whileStmt   : 'while' '(' expr ')' ':' block ;

forStmt
    : 'for' type? ID '(' expr ',' expr ',' expr ')' ':'
        block ;

foreachStmt
    : 'foreach' type? ID '(' ID ')' ':'
     block;

printStmt   : 'print' '(' expr ')' NL ;     //funkcja print
returnStmt  : '=>' expr NL ;                //wyrażenie zwracane
emptyLine   : NL ;                          //pusta linia

expr        : logicOr ;                     //wyrażenie


//operatory logiczne
logicOr     : logicAnd ( 'Or'  logicAnd )* ;
logicAnd    : equality ( 'And' equality )* ;
equality    : compare  ( ('=='|'!='|'>='|'<='|'>'|'<') compare )* ;

//operatory matematyczne
compare     : addSub ;
addSub      : mulDiv  ( ('+'|'-') mulDiv)* ;
mulDiv      : power   ( ('*'|'/'|'//') power)* ;
power       : unary   ( '^' unary )* ; //potęgowanie

unary                   //pojedncze wyrażenie
    : dottedID '?' ID
    | ('Not'|'-'|'+') unary //uwzględniamy znaki przed wyrażeniem
    | atom
    ;

vector      : '[' expr (',' expr)* ']' ;    //tablica jednowymiarowa

atom        //wartość atomiczna
    : INT
    | FLOAT
    | BOOLEAN
    | 'parent' '::' atom
    | (dottedID ('->' ID ('[' expr ']')?)?) ('(' argList? ')')?
    | vector
    | '(' expr ')' ;

argList     : expr (',' expr)* ;        //lista argumentów (np. funkcji)

type        : 'particle' | 'field' | 'system'   //typ zmiennej
            | 'float' | 'int' | 'bool' ;

returnType      //typ zwracany
    : type                                             
    ;

block           : INDENT statement+ DEDENT ;    //blok kodu

BOOLEAN     : 'True'|'False';                   //wartości logiczne
ID : ('$'? [\p{L}_]) [\p{L}\p{N}_]* ;


INT         : [0-9]+ ;                      //wartości numeryczne całkowite
FLOAT       : [0-9]+ '.' [0-9]* ;           //wartości numeryczne zmiennoprzecikowe

COMMENT         : '%' ~[\r\n]* -> skip ;    //komentarze
WS              : [ \t\f]+ -> skip;         //puste znaki

NL: ('\r'? '\n' ' '*);      //new line - token potrzebny do obsługi wcięć


dottedID    : ID ('.' ID)* |                //odwołanie do identyfikatora
               'parent::' dottedID;