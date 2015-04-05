import pygame
import bobj
from star import Star


green = 0, 255, 0
blue = 0, 0, 255
red = 255, 0, 0


##########################################################################
class StarSystem(bobj.BaseObj):
    def __init__(self, loc):
        self.numstars = self.genStarNum()
        self.numstars = 1             # Keep it simple
        self.location = loc
        self.starlist = []
        for i in range(self.numstars):
            self.starlist.append(Star(loc))
        self.basecolor = None

    ##########################################################################
    def Plot(self, surf):
        radius = 2
        color = None
        for star in self.starlist:
            radius = 2
            for planet in star.planets():
                if planet.homeplanet:
                    color = (250, 250, 10)
                elif planet.population > 0 and not color:
                    color = green
                elif planet.popcapacity > 0 and not color:
                    color = blue
                radius = max(radius, int(planet.population / 1E9))
        if not color:
            color = red

        pygame.draw.circle(surf, color, abs(self.location), radius, 0)

    ##########################################################################
    def stars(self):
        return self.starlist

    ##########################################################################
    def __len__(self):
        return len(self.starlist)

    ##########################################################################
    def __repr__(self):
        str = ""
        for i in self.starlist:
            str += "%s " % repr(i)
        return "<StarSystem %s: %s>" % (self.location, str)

    ##########################################################################
    def genStarNum(self):
        x = self.d6(2)
        if 2 <= x <= 10:
            return 1
        elif x == 11:
            return 2
        elif x == 12:
            return 3
        else:
            print "x=%d" % x

# EOF
