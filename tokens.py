#########################
# CONSTANTS
#########################
import string

DIGITS = "0123456789"
LETTERS = string.ascii_letters
ALPHANUMERIC = LETTERS + DIGITS
UNDERSCORE_ALPHANUMERIC = ALPHANUMERIC + "_"
KEYWORDS = [
    "VAR"
]


class TokenTypes:
    TT_INT = "TT_INT"
    TT_FLOAT = "FLOAT"
    TT_IDENTIFIER = "IDENTIFIER"
    TT_KEYWORD = "KEYWORD"
    TT_PLUS = "PLUS"
    TT_MINUS = "MINUS"
    TT_MUL = "MUL"
    TT_DIV = "DIV"
    TT_POWER = "POWER"
    TT_EQ = "EQ"
    TT_LPAREN = "LPAREN"
    TT_RPAREN = "RPAREN"
    TT_EOF = "EOF"


#########################
# TOKEN
#########################

class TokenObj:
    def __init__(self, t_type, t_value=None, start_pos=None, end_pos=None):
        self._type = t_type
        self._value = t_value
        if start_pos:
            self._start_pos = start_pos.copy()
            self._end_pos = start_pos.copy()
            self._end_pos.advance()
        if end_pos:
            self._end_pos = end_pos.copy()

    def get_type(self):
        return self._type

    def get_value(self):
        return self._value

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def matches(self, token_type, value):
        return self._type == token_type and self._value == value

    def __repr__(self):
        repr_str = f"{self._type}"
        if self._value:
            repr_str = f"{self._type}: {self._value}"
        return repr_str
