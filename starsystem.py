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
        if not self.basecolor:
            color = None
            for star in self.starlist:
                for planet in star.planets():
                    if planet.population > 0:
                        color = green
                        self.basecolor = color = green
                        break
                    elif planet.popcapacity > 0 and not color:
                        color = blue
                        break
            if not color:
                self.basecolor = color = red
        else:
            color = self.basecolor

        pygame.draw.circle(surf, color, abs(self.location), 2, 0)

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
