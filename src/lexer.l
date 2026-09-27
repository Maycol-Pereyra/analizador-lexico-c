%{
#include <stdio.h>
#include <string.h>

static int col = 1;

static void emit(const char *type) {
    printf("%s|%s|%d|%d\n", type, yytext, yylineno, col);
    col += (int)strlen(yytext);
}
%}

%option noyywrap
%option yylineno
%option nounistd

%%

"if"|"else"|"while"|"for"|"int"|"float"|"char"|"void"|"return"   { emit("PALABRA_CLAVE"); }

[a-zA-Z_][a-zA-Z0-9_]*        { emit("IDENTIFICADOR"); }

[0-9]+\.[0-9]+                { emit("DECIMAL"); }
[0-9]+                        { emit("ENTERO"); }

\"([^\"\\\n]|\\.)*\"          { emit("CADENA"); }

"=="|"!="|"<="|">="|"&&"|"\|\|"|"+"|"-"|"*"|"/"|"%"|"="|"<"|">"|"!"   { emit("OPERADOR"); }

"{"|"}"|"("|")"|";"|","       { emit("SIMBOLO"); }

"//"[^\n]*                    { /* comentario de linea: se descarta */ }
"/*"([^*]|\*+[^*/])*\*+"/"    { /* comentario de bloque: se descarta */ }

\"([^\"\\\n]|\\.)*             { emit("ERROR"); }

\n                             { col = 1; }
[ \t\r]+                       { col += (int)yyleng; }

.                               { emit("ERROR"); }

%%
