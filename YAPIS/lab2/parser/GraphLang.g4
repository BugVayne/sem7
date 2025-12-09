// Файл: GraphLang.g4
grammar GraphLang;

// Стартовое правило: программа - это последовательность стейтментов
program: statement* EOF;

// Стейтмент - это одна из команд языка
statement:
      declaration
    | assignment
    | if_stmt
    | switch_stmt
    | until_stmt
    | function_def
    | return_stmt
    | expr ';' // Вызов процедуры, например write(...);
    ;

// Блок кода - ноль или более стейтментов в фигурных скобках
block: '{' statement* '}';

// Объявление: graph g; или list<node> path;
declaration: type ID ';';

// Присваивание: g = create_graph();
assignment: ID '=' expr ';';

// Условный оператор
if_stmt: IF '(' expr ')' THEN block (ELSE block)?;

// Switch-кейс. Обратите внимание, что кейсы не требуют скобок.
switch_stmt: SWITCH '(' expr ')' '{' case_block* default_block? '}';
case_block: CASE literal ':' statement*;
default_block: DEFAULT ':' statement*;

// Цикл until
until_stmt: UNTIL '(' expr ')' block;

// Определение функции/процедуры
function_def: type ID LPAREN param_list? RPAREN block;
param_list: param (',' param)*;
param: REF? type ID; // Поддержка ref-параметров

// Оператор return
return_stmt: RETURN expr ';';

// Правила для выражений с метками для Visitor'а и учетом приоритетов
expr:
      expr OR expr                            # OrExpr
    | expr ('==' | '!=' | '>=' | '>') expr      # CmpExpr
    | expr ('+' | '-') expr                   # AddSubExpr
    | '!' expr                                # NotExpr
    | primary                                 # PrimaryExpr
    ;

// "Первичные" выражения - самые высокоприоритетные
primary:
      ID LPAREN arg_list? RPAREN          # FuncCallExpr
    | primary LBRACK expr RBRACK        # IndexExpr
    | ID                                  # IdExpr
    | literal                             # LiteralExpr
    | LPAREN expr RPAREN                  # ParenExpr
    ;

arg_list: expr (',' expr)*;

// Типы, включая обобщенные (list<node>)
type: simple_type ('<' type '>')? | VOID;
simple_type: GRAPH | NODE | ARC | LIST | INT | BOOL | FLOAT;

// Литералы
literal: FLOAT_LIT | INT_LIT | STRING_LIT | NULL;

// --- ПРАВИЛА ЛЕКСЕРА (ТОКЕНЫ) ---

// Ключевые слова (обязательно перед ID)
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

// Идентификаторы
ID: [a-zA-Z_][a-zA-Z0-9_]*;

// Литералы
FLOAT_LIT: [0-9]+ '.' [0-9]* | '.' [0-9]+;
INT_LIT: [0-9]+;
STRING_LIT: '"' (~["\\] | '\\' .)* '"';

// Символы и операторы
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

// Пропускаемые символы
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;