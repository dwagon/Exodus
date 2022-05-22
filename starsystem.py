import pygame
import bobj
from star import Star


green = 0, 255, 0
blue = 0, 0, 255
red = 255, 0, 0
yellow = 255, 255, 0
white = 255, 255, 255


##########################################################################
class StarSystem(bobj.BaseObj):
    def __init__(self, loc):
        self.numstars = self.genStarNum()
        self.numstars = 1  # Keep it simple
        self.location = loc
        self.starlist = []
        for i in range(self.numstars):
            self.starlist.append(Star(loc))
        self.basecolor = None

    ##########################################################################
    def Plot(self, surf):
        pop = 0
        homesystem = False
        popcap = 0
        maxdist = 0
        for star in self.starlist:
            for planet in star.planets():
                if planet.homeplanet:
                    homesystem = True
                if planet.maxdist:
                    maxdist = max(maxdist, planet.maxdist)
                pop = max(planet.population, pop)
                popcap += planet.popcapacity

        if homesystem:
            color = yellow
        elif pop > 0:
            color = green
        elif popcap > 0:
            color = blue
        else:
            color = red
        if pop > 1e9:
            radius = 6
        elif pop > 1e8:
            radius = 5
        elif pop > 1e7:
            radius = 4
        elif pop > 1e6:
            radius = 3
        else:
            radius = 2

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
            print("x=%d" % x)


# EOF
