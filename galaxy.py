import coord
from starsystem import StarSystem
from bobj import BaseObj


##########################################################################
class Galaxy(BaseObj):
    def __init__(self, width=1000, height=100):
        self.starbits = []
        self.initialise(width, height)
        self.width = width
        self.height = height
        self.genPlanetList()
        self.terrestrials = self.getTerrestrials()

    ##########################################################################
    def click(self, pos):
        for x in (0, -1, 1, -2, 2):
            for y in (0, -1, 1, -2, 2):
                foo = self[coord.Coord(pos[0]+x, pos[1]+y)]
                if foo:
                    return foo

    ##########################################################################
    def genPlanetList(self):
        tmp = []
        for starsys in self.starsystems():
            for star in starsys.stars():
                for planet in star.planets():
                    tmp.append(planet)
        self.planetlist = tmp

    ##########################################################################
    def starsystems(self):
        return self.starbits

    ##########################################################################
    def __getitem__(self, loc):
        for starsystem in self.starbits:
            if starsystem.location == loc:
                return starsystem

    ##########################################################################
    def Plot(self, surf):
        print "Plot(Galaxy)"
        pass

    ##########################################################################
    def initialise(self, width, height):
        numstars = 0
        for x in range(width):
            for y in range(height):
                loc = coord.Coord(x, y)
                if self.d6(2) >= 11 and self.d6(2) >= 11 and self.d6(2) >= 11:
                    ss = StarSystem(loc)
                    self.starbits.append(ss)
                    numstars += len(ss)
        print "NumStars=%d" % numstars

    ##########################################################################
    def getTerrestrials(self, planetlist=None):
        tmp = []
        if planetlist:
            for planet in planetlist:
                if planet.popcapacity > 0:
                    tmp.append(planet)
        else:
            for starsys in self.starsystems():
                for star in starsys.stars():
                    for planet in star.planets():
                        if planet.popcapacity > 0:
                            tmp.append(planet)
        return tmp

    ##########################################################################
    def findHomePlanet(self):
        cent = coord.Coord(self.width / 2, self.height / 2)
        mindist = self.width * self.height
        homeplanet = None
        for planet in self.terrestrials:
            if planet.popcapacity > 1e9:
                dist = planet.location.distance(cent)
                if dist < mindist:
                    mindist = dist
                    homeplanet = planet

        print "Homeplanet=%s" % str(homeplanet)
        homeplanet.population = int(homeplanet.popcapacity * 0.5)
        homeplanet.homeplanet = True
        homeplanet.settledate = -500
        return homeplanet

# EOF
