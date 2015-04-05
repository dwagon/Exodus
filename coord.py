import math
from game import screenwidth, screenheight, galaxyradius
from bobj import BaseObj


##########################################################################
class Coord(BaseObj):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    ##########################################################################
    def coords(self):
        return (self.x, self.y)

    ##########################################################################
    def __ne__(self, loc):
        return (self.x != loc.x or self.y != loc.y)

    ##########################################################################
    def __eq__(self, loc):
        return (self.x == loc.x and self.y == loc.y)

    ##########################################################################
    def __nonzero__(self):
        return self.x != 0 or self.y != 0

    ##########################################################################
    def distance(self, loc):
        dist = math.sqrt((self.x - loc.x) ** 2 + (self.y - loc.y) ** 2)
        return dist

    ##########################################################################
    def __abs__(self):
        x = self.x * float(screenwidth) / galaxyradius
        y = self.y * float(screenheight) / galaxyradius
        return (int(x) + 1, int(y) + 1)

    ##########################################################################
    def __repr__(self):
        return "<Coord %d, %d>" % (self.x, self.y)

# EOF
