import math
from config import screenwidth, screenheight, galaxywidth, galaxyheight
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
        return self.x != loc.x or self.y != loc.y

    ##########################################################################
    def __eq__(self, loc):
        return self.x == loc.x and self.y == loc.y

    ##########################################################################
    def __nonzero__(self):
        return self.x != 0 or self.y != 0

    ##########################################################################
    def distance(self, loc):
        dist = math.sqrt((self.x - loc.x) ** 2 + (self.y - loc.y) ** 2)
        return dist

    ##########################################################################
    def angle(self, loc):
        return math.atan2((loc.y - self.y), (loc.x - self.x))

    ##########################################################################
    def vector(self, angle, dist):
        x = self.x + math.cos(angle) * dist
        y = self.y + math.sin(angle) * dist
        return Coord(x, y)

    ##########################################################################
    def __abs__(self):
        x = self.x * float(screenwidth) / galaxywidth
        y = self.y * float(screenheight) / galaxyheight
        return (int(x) + 1, int(y) + 1)

    ##########################################################################
    def __repr__(self):
        return "<Coord %d, %d>" % (self.x, self.y)


# EOF
