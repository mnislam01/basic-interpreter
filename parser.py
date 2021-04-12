##################
# PARSER
##################

"""
The idea of the parser is to build a syntax tree of the program
from the tokens created by the lexer

Example 01:
    We have this expression below
    >> 1 + 2 * 3
    This expression is tokenized by the lexer as following
    >> [TT_INT: 1, PLUS, TT_INT: 2, MUL, TT_INT: 3]

    From this tokenized expression the parser will generate this syntax tree

                            Binary Operator (PLUS)
                                    |
                            _________________
                            |               |
                        Number (1)     Binary Operator (MUL)
                                                |
                                        ______________________
                                        |                    |
                                    Number (2)          Number (3)


As you can see, this binary tree give you the idea exactly which operations to perform
and gives you the exact order


Example 02:
    Let's take the same expression except that 1 + 2 are in between the parenthesis
    >> (1 + 2) * 3

    Tokenized by lexer like the following
    >> [LPARAM, TT_INT: 1, PLUS, TT_INT: 2, RPARAM, MUL, TT_INT: 3]

    Now this causes the order of the tree to change quite completely different

                            Binary Operator (MUL)
                                      |
                    -----------------------------------
                    |                                 |
            Binary Operator (PLUS)                Number (3)
                    |
            -------------------
            |                    |
        Number (1)          Number (2)


So, what the parser has to do is to figure out if the tokens match our language grammar.
And if it does generate a tree accordingly
"""

###########################################
#               Nodes
###########################################

from errors import InvalidSyntaxError
from tokens import TokenTypes


class NumberNode:
    def __init__(self, token):
        self._token = token
        self._start_pos = self._token.get_start_pos()
        self._end_pos = self._token.get_end_pos()

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def get_token(self):
        return self._token

    def __repr__(self):
        return f"{self._token}"


class VariableAccessNode:
    def __init__(self, variable_name_token):
        self._variable_name_token = variable_name_token
        self._start_pos = self._variable_name_token.get_start_pos()
        self._end_pos = self._variable_name_token.get_end_pos()

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def get_token(self):
        return self._variable_name_token


class VariableAssignNode:
    def __init__(self, variable_name_token, value_node):
        self._variable_name_token = variable_name_token
        self._value_node = value_node
        self._start_pos = self._variable_name_token.get_start_pos()
        self._end_pos = self._value_node.get_end_pos()

    def get_token(self):
        return self._variable_name_token

    def get_value_node(self):
        return self._value_node

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos


class UnaryOpNode:
    def __init__(self, operator_token, node):
        self._operator_token = operator_token
        self._node = node
        self._start_pos = self._operator_token.get_start_pos()
        self._end_pos = self._operator_token.get_end_pos()

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def get_token(self):
        return self._operator_token

    def __repr__(self):
        return f"({self._operator_token}, {self._node})"


class BinaryOpNode:
    def __init__(self, left_node, operator_token, right_node):
        self._left_node = left_node
        self._operator_token = operator_token
        self._right_node = right_node
        self._start_pos = self._left_node.get_end_pos()
        self._end_pos = self._right_node.get_end_pos()

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def get_token(self):
        return self._operator_token

    def get_left_node(self):
        return self._left_node

    def get_right_node(self):
        return self._right_node

    def __repr__(self):
        return f"({self._left_node}, {self._operator_token}, {self._right_node})"


class ParseResult:
    def __init__(self):
        self._error = None
        self._node = None
        self._advance_count = 0

    def register_advancement(self):
        self._advance_count += 1

    def register(self, res):
        self._advance_count += res._advance_count
        if res._error:
            self._error = res._error
        return res._node

    def success(self, node):
        self._node = node
        return self

    def failed(self, error):
        if not self._error or self._advance_count == 0:
            self._error = error
        return self


class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._token_indx = -1
        self.current_token = None
        self.advance()

    def binary_operation(self, function_a, operation_tokens, function_b=None):
        if function_b == None:
            function_b = function_a
        res = ParseResult()
        left_factor = res.register(function_a())
        if res._error:
            return res

        while self.current_token._type in operation_tokens:
            operator_token = self.current_token
            res.register_advancement()
            self.advance()
            right_factor = res.register(function_b())
            if res._error:
                return res
            left_factor = BinaryOpNode(left_factor, operator_token, right_factor)
        return res.success(left_factor)

    def atom(self):
        res = ParseResult()
        token = self.current_token

        if token._type in [TokenTypes.TT_INT, TokenTypes.TT_FLOAT]:
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(token))

        elif token.get_type() == TokenTypes.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VariableAccessNode(token))

        elif token._type == TokenTypes.TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expression())
            if res._error:
                return res
            if self.current_token._type == TokenTypes.TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failed(
                    InvalidSyntaxError(
                        self.current_token._start_pos, self.current_token._end_pos,
                        "Expected ')'"
                    )
                )
        return res.failed(
            InvalidSyntaxError(
                self.current_token._start_pos, self.current_token._end_pos,
                "Expected INT, FLOAT, IDENTIFIER, '+', '-', '*' or '('"
            )
        )

    def power(self):
        return self.binary_operation(self.atom, [TokenTypes.TT_POWER], self.factor)

    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token._type in [TokenTypes.TT_PLUS, TokenTypes.TT_MINUS]:
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res._error:
                return res
            return res.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self):
        return self.binary_operation(self.factor, [TokenTypes.TT_MUL, TokenTypes.TT_DIV])

    def expression(self):
        res = ParseResult()
        if self.current_token.matches(TokenTypes.TT_KEYWORD, "VAR"):
            res.register_advancement()
            self.advance()

            if self.current_token.get_type() != TokenTypes.TT_IDENTIFIER:
                res.failed(
                    InvalidSyntaxError(
                        self.current_token.get_start_pos(), self.current_token.get_end_pos(),
                        "Expected identifier"
                    )
                )
            var_name = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token.get_type() != TokenTypes.TT_EQ:
                res.failed(
                    InvalidSyntaxError(
                        self.current_token.get_start_pos(), self.current_token.get_end_pos(),
                        "Expected '='"
                    )
                )
            res.register_advancement()
            self.advance()

            expr = res.register(self.expression())
            if res._error:
                return res
            return res.success(VariableAssignNode(var_name, expr))

        node = res.register(self.binary_operation(self.term, [TokenTypes.TT_PLUS, TokenTypes.TT_MINUS]))
        if res._error:
            return res.failed(
                InvalidSyntaxError(
                    self.current_token._start_pos, self.current_token._end_pos,
                    "Expected VAR, int, float, identifier, '+', '-', '*' or '('"
                )
            )
        return res.success(node)

    def advance(self):
        self._token_indx += 1
        if self._token_indx < len(self._tokens):
            self.current_token = self._tokens[self._token_indx]
        return self.current_token

    def parse(self):
        res = self.expression()
        if not res._error and self.current_token._type != TokenTypes.TT_EOF:
            return res.failed(
                InvalidSyntaxError(
                    self.current_token._start_pos, self.current_token._end_pos,
                    "Expected '+', '-', '*' or '/'"
                )
            )
        return res


def exec_parser(tokens):
    parser = Parser(tokens)
    ast = parser.parse()
    return ast
