grammar GraphLang;

// --- ПРАВИЛА ПАРСЕРА ---

program: statement* EOF;

statement:
      declaration
    | assignment
    | if_stmt
    | switch_stmt
    | until_stmt
    | function_def
    | return_stmt
    | expr ';'
    ;

block: '{' statement* '}';

declaration: type ID ';';

assignment: ID '=' expr ';';

if_stmt: IF '(' expr ')' THEN block (ELSE block)?;

switch_stmt: SWITCH '(' expr ')' '{' case_block* default_block? '}';
case_block: CASE literal ':' statement*;
default_block: DEFAULT ':' statement*;

until_stmt: UNTIL '(' expr ')' block;

function_def: type ID LPAREN param_list? RPAREN block;
param_list: param (',' param)*;
param: REF? type ID;

return_stmt: RETURN expr ';';

expr:
      expr OR expr                            # OrExpr
    | expr ('==' | '!=' | '>=' | '>') expr    # CmpExpr
    | expr ('+' | '-') expr                   # AddSubExpr
    | '!' expr                                # NotExpr
    | primary                                 # PrimaryExpr
    ;

primary:
      ID LPAREN arg_list? RPAREN          # FuncCallExpr
    | primary LBRACK expr RBRACK          # IndexExpr
    | ID                                  # IdExpr
    | literal                             # LiteralExpr
    | LPAREN expr RPAREN                  # ParenExpr
    ;

arg_list: expr (',' expr)*;

type: simple_type ('<' type '>')? | VOID;
simple_type: GRAPH | NODE | ARC | LIST | INT | BOOL | FLOAT;

// !!! ИСПРАВЛЕНИЕ ЗДЕСЬ: Добавлено | BOOL_LIT !!!
literal: FLOAT_LIT | INT_LIT | STRING_LIT | BOOL_LIT | NULL;

// --- ПРАВИЛА ЛЕКСЕРА ---

GRAPH: 'graph';
NODE: 'node';
ARC: 'arc';
LIST: 'list';
INT: 'int';
BOOL: 'bool';
FLOAT: 'float';
VOID: 'void';
IF: 'if';
THEN: 'then';
ELSE: 'else';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
UNTIL: 'until';
RETURN: 'return';
NULL: 'null';
REF: 'ref';

// Токен для true/false
BOOL_LIT: 'true' | 'false';

ID: [a-zA-Z_][a-zA-Z0-9_]*;

FLOAT_LIT: [0-9]+ '.' [0-9]* | '.' [0-9]+;
INT_LIT: [0-9]+;
STRING_LIT: '"' (~["\\] | '\\' .)* '"';

ASSIGN: '=';
GT: '>';
GTE: '>=';
EQ: '==';
NEQ: '!=';
OR: '||';
NOT: '!';
PLUS: '+';
MINUS: '-';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
SEMI: ';';
COMMA: ',';

WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;