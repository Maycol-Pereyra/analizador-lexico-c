#include <stdio.h>

extern int yylex(void);
extern FILE *yyin;

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "uso: lexer.exe <archivo>\n");
        return 1;
    }
    yyin = fopen(argv[1], "r");
    if (!yyin) {
        fprintf(stderr, "no se pudo abrir: %s\n", argv[1]);
        return 1;
    }
    yylex();
    fclose(yyin);
    return 0;
}
