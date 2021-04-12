#########################
# LEXER
#########################


from errors import (
    IllegalCharError
)
from position import Position
from tokens import (
    DIGITS,
    LETTERS,
    ALPHANUMERIC,
    KEYWORDS,
    UNDERSCORE_ALPHANUMERIC,
    TokenTypes,
    TokenObj
)


class Lexer:
    def __init__(self, f_name: str, text: str):
        self._f_name = f_name
        self._text = text
        self.pos: Position = Position(-1, 0, -1, f_name, text)
        self.current_char: None = None
        self.advance()

    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = self._text[self.pos._indx] if self.pos._indx < len(self._text) else None

    def make_number(self) -> TokenObj:
        num_str = ""
        dot_count = 0
        start_pos = self.pos.copy()
        while self.current_char is not None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return TokenObj(TokenTypes.TT_INT, int(num_str), start_pos=start_pos, end_pos=self.pos)
        else:
            return TokenObj(TokenTypes.TT_FLOAT, float(num_str), start_pos=start_pos, end_pos=self.pos)

    def make_identifier(self):
        iden_str = ""
        start_pos = self.pos.copy()

        while self.current_char is not None and self.current_char in UNDERSCORE_ALPHANUMERIC:
            iden_str += self.current_char
            self.advance()
        token_type = TokenTypes.TT_KEYWORD if iden_str in KEYWORDS else TokenTypes.TT_IDENTIFIER
        return TokenObj(token_type, iden_str, start_pos=start_pos, end_pos=self.pos)

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == "+":
                tokens.append(TokenObj(TokenTypes.TT_PLUS, start_pos=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(TokenObj(TokenTypes.TT_MINUS, start_pos=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(TokenObj(TokenTypes.TT_MUL, start_pos=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(TokenObj(TokenTypes.TT_DIV, start_pos=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(TokenObj(TokenTypes.TT_POWER, start_pos=self.pos))
                self.advance()
            elif self.current_char == "=":
                tokens.append(TokenObj(TokenTypes.TT_EQ, start_pos=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(TokenObj(TokenTypes.TT_LPAREN, start_pos=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(TokenObj(TokenTypes.TT_RPAREN, start_pos=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(TokenObj(TokenTypes.TT_EOF, start_pos=self.pos))
        return tokens, None


def exec_lexer(f_name, text):
    lexer = Lexer(f_name, text)
    return lexer.make_tokens()
