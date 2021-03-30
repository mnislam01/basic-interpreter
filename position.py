########################
# Position
########################

class Position:
    def __init__(self, indx, ln_num, col_num, f_name, f_txt):
        self._indx = indx
        self._ln_num = ln_num
        self._col_num = col_num
        self._f_name = f_name
        self._f_txt = f_txt

    def advance(self, current_char=None):
        self._indx += 1
        self._col_num += 1

        if current_char == "\n":
            self._ln_num += 1
            self._col_num = 0
        return self

    def copy(self):
        return Position(self._indx, self._ln_num, self._col_num, self._f_name, self._f_txt)
