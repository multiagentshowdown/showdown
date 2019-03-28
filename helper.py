class loc:
    def __init__(self, _r, _c):
        self.r = _r
        self.c = _c
    def __eq__(self, other):
        return (self.r == other.r) and (self.c == other.c)
    def __ne__(self, other):
        return not((self.r == other.r) and (self.c == other.c))
    def __add__(self, other):
        return loc((self.r + other.r), (self.c + other.c))
    def __sub__(self, other):
        return loc((self.r - other.r), (self.c - other.c))
    def __str__(self):
        return '(%s, %s)' % (self.r, self.c)
    def __repr__(self):
        return '(%s, %s)' % (self.r, self.c)
    def tuple(self):
        return (self.r, self.c)
