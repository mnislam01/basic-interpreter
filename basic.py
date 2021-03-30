import lexer
import parser
import interpreter


def run(f_name, text):
    tokens, token_error = lexer.exec_lexer(f_name, text)
    if token_error:
        return None, token_error
    ast = parser.exec_parser(tokens)
    if ast._error:
        return None, ast._error
    result, error = interpreter.exec_interpreter(ast)
    return result, error
