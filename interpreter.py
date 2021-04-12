from errors import RTError
from tokens import TokenTypes


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self._display_name = display_name
        self._parent = parent
        self._parent_entry_pos = parent_entry_pos
        self._symbol_table = None


class Number:
    def __init__(self, value):
        self._value = value
        self._start_pos = None
        self._end_pos = None
        self._context = None
        # self.set_position()
        # self.set_context()

    def set_position(self, start_pos=None, end_pos=None):
        self._start_pos = start_pos
        self._end_pos = end_pos
        return self

    def set_context(self, context=None):
        self._context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self._value + other._value).set_context(self._context), None

    def sub_by(self, other):
        if isinstance(other, Number):
            return Number(self._value - other._value).set_context(self._context), None

    def mul_by(self, other):
        if isinstance(other, Number):
            return Number(self._value * other._value).set_context(self._context), None

    def div_by(self, other):
        if isinstance(other, Number):
            if other._value == 0:
                return None, RTError(
                    other._start_pos, other._end_pos,
                    "Division by Zero",
                    self._context
                )
            return Number(self._value / other._value).set_context(self._context), None

    def pow_by(self, other):
        if isinstance(other, Number):
            return Number(self._value ** other._value).set_context(self._context), None

    def copy(self):
        copy = Number(self._value)
        copy.set_position(self._start_pos, self._end_pos)
        copy.set_context(self._context)
        return copy

    def __repr__(self):
        return str(self._value)


class SymbolTable:
    def __init__(self):
        self._symbols = {}
        self._parent = None

    def get(self, variable_name):
        value = self._symbols.get(variable_name, None)
        if value is None and self._parent:
            return self._parent.get(variable_name, None)
        return value

    def set(self, variable_name, value):
        self._symbols[variable_name] = value

    def remove(self, variable_name):
        del self._symbols[variable_name]


class RuntimeResult:
    def __init__(self):
        self._value = None
        self._error = None

    def register(self, res):
        if res._error:
            self._error = res._error
        return res._value

    def success(self, value):
        self._value = value
        return self

    def failed(self, error):
        self._error = error
        return self


class Interpreter:

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_NumberNode(self, node, context):
        token = node.get_token()
        return RuntimeResult().success(
            Number(token.get_value()).set_context(context).set_position(node.get_start_pos(), node.get_end_pos())
        )

    def visit_VariableAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.get_token().get_value()
        value = res.register(self.interpret(node.get_value_node(), context))
        if res._error:
            return res
        context._symbol_table.set(var_name, value)
        return res.success(value)

    def visit_VariableAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.get_token().get_value()
        value = context._symbol_table.get(var_name)
        if not value:
            return res.failed(RTError(node.get_start_pos(), node.get_end_pos(),
                                      f"'{var_name}' is not defined.", context))
        value = value.copy().set_position(node.get_start_pos(), node.get_end_pos())
        return res.success(value)

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.interpret(node._node, context))
        if res._error:
            return res
        token = node.get_token()
        error = None
        if token.get_type() == TokenTypes.TT_MINUS:
            number, error = number.mul_by(Number(-1))
        if error:
            return res.failed(error)
        else:
            return res.success(number.set_position(node.get_start_pos(), node.get_end_pos()))

    def visit_BinaryOpNode(self, node, context):
        res = RuntimeResult()
        left = res.register(self.interpret(node.get_left_node(), context))
        if res._error:
            return res
        right = res.register(self.interpret(node.get_right_node(), context))
        if res._error:
            return res

        token = node.get_token()
        if token.get_type() == TokenTypes.TT_PLUS:
            result, error = left.added_to(right)
        elif token.get_type() == TokenTypes.TT_MINUS:
            result, error = left.sub_by(right)
        elif token.get_type() == TokenTypes.TT_MUL:
            result, error = left.mul_by(right)
        elif token.get_type() == TokenTypes.TT_DIV:
            result, error = left.div_by(right)
        elif token.get_type() == TokenTypes.TT_POWER:
            result, error = left.pow_by(right)

        if error:
            return res.failed(error)
        else:
            return res.success(result.set_position(node.get_start_pos(), node.get_end_pos()))

    def interpret(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)


GLOBAL_SYMBOL_TABLE = SymbolTable()
GLOBAL_SYMBOL_TABLE.set("null", Number(0))


def exec_interpreter(abstract_syntax_tree):
    interpreter = Interpreter()
    context = Context('<program>')
    context._symbol_table = GLOBAL_SYMBOL_TABLE
    result = interpreter.interpret(abstract_syntax_tree._node, context)
    return result._value, result._error
