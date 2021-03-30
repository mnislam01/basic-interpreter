###################
# ERRORS
####################

from helpers import string_with_arrows


class Error:
    def __init__(self, pos_start, pos_end, err_name, err_details):
        self._pos_start = pos_start
        self._pos_end = pos_end
        self._err_name = err_name
        self._err_details = err_details

    def as_string(self):
        string = f"{self._err_name}: {self._err_details}."
        string += f"\nFile {self._pos_start._f_name}, line {self._pos_start._ln_num + 1}"
        string += "\n" + string_with_arrows(self._pos_start._f_txt, self._pos_start, self._pos_end)
        return string


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        self._context = context
        super().__init__(pos_start, pos_end, "Runtime Error", details)

    def generate_traceback(self):
        result = ""
        pos = self._pos_start
        cntxt = self._context
        while cntxt:
            result = f"  File {pos._f_name}, line {str(pos._ln_num + 1)}, in {cntxt._display_name}\n" + result
            pos = cntxt._parent_entry_pos
            cntxt = cntxt._parent

        return "Traceback (most recent call last):\n" + result

    def as_string(self):
        string = self.generate_traceback()
        string += f"{self._err_name}: {self._err_details}."
        string += "\n" + string_with_arrows(self._pos_start._f_txt, self._pos_start, self._pos_end)
        return string
