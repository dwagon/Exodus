import math
from game import screenwidth, screenheight, galaxyradius
from bobj import BaseObj


##########################################################################
class Coord(BaseObj):
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    ##########################################################################
    def coords(self):
        return (self.x, self.y, self.z)

    ##########################################################################
    def __ne__(self, loc):
        return (self.x != loc.x or self.y != loc.y or self.z != loc.z)

    ##########################################################################
    def __eq__(self, loc):
        return (self.x == loc.x and self.y == loc.y and self.z == loc.z)

    ##########################################################################
    def __nonzero__(self):
        return self.x != 0 or self.y != 0 or self.z != 0

    ##########################################################################
    def distance(self, loc):
        # dist=abs(self.x-loc.x)+abs(self.y-loc.y)+abs(self.z-loc.z)
        dist = math.sqrt(
            (self.x - loc.x) ** 2 + (self.y - loc.y) ** 2 + (self.z - loc.z) ** 2)
        return dist

    ##########################################################################
    def __abs__(self):
        x = self.x * float(screenwidth) / galaxyradius
        y = self.y * float(screenheight) / galaxyradius
        return (int(x) + 1, int(y) + 1)

    ##########################################################################
    def __repr__(self):
        return "<Coord %d, %d, %d>" % (self.x, self.y, self.z)

# EOF
