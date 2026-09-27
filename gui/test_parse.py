import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.app import parse_token_line


def test_parse_simple_token():
    assert parse_token_line("IDENTIFICADOR|contador|3|5") == ("IDENTIFICADOR", "contador", "3", "5")


def test_parse_token_with_pipe_in_lexeme():
    # una cadena podria contener el caracter '|': se debe unir todo lo sobrante en el lexema
    assert parse_token_line('CADENA|"a|b"|1|1') == ("CADENA", '"a|b"', "1", "1")


def test_parse_empty_line_returns_none():
    assert parse_token_line("") is None
    assert parse_token_line("   ") is None


if __name__ == "__main__":
    test_parse_simple_token()
    test_parse_token_with_pipe_in_lexeme()
    test_parse_empty_line_returns_none()
    print("TODOS LOS TESTS PASARON")
