from coord import Coord
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
        print("%d terrestrials" % len(self.terrestrials))
        self.gasgiants = self.getGasGiants()
        print("%d gasgiants" % len(self.gasgiants))

    ##########################################################################
    def click(self, pos):
        for x in (0, -1, 1, -2, 2, -3, 3):
            for y in (0, -1, 1, -2, 2, -3, 3):
                foo = self[Coord(pos[0] + x, pos[1] + y)]
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
        print("Plot(Galaxy)")
        pass

    ##########################################################################
    def initialise(self, width, height):
        numstars = 0
        for x in range(width):
            for y in range(height):
                loc = Coord(x, y)
                if self.d6(2) >= 11 and self.d6(2) >= 11 and self.d6(2) >= 11:
                    ss = StarSystem(loc)
                    self.starbits.append(ss)
                    numstars += len(ss)
        print("NumStars=%d" % numstars)

    ##########################################################################
    def getTerrestrials(self, planetlist=[]):
        tmp = []
        if not planetlist:
            for starsys in self.starsystems():
                for star in starsys.stars():
                    for planet in star.planets():
                        planetlist.append(planet)
        for planet in planetlist:
            if planet.popcapacity > 0:
                tmp.append(planet)
        return tmp

    ##########################################################################
    def getGasGiants(self, planetlist=[]):
        tmp = []
        if not planetlist:
            for starsys in self.starsystems():
                for star in starsys.stars():
                    for planet in star.planets():
                        planetlist.append(planet)
        for planet in planetlist:
            if planet.plantype == "gasgiant":
                tmp.append(planet)
        return tmp

    ##########################################################################
    def findHomePlanet(self):
        cent = Coord(self.width / 2, self.height / 2)
        mindist = self.width * self.height
        homeplanet = None
        for planet in self.terrestrials:
            if planet.popcapacity > 1e9:
                dist = planet.location.distance(cent)
                if dist < mindist:
                    mindist = dist
                    homeplanet = planet

        homeplanet.population = int(homeplanet.popcapacity * 0.9)
        homeplanet.homeplanet = True
        homeplanet.settledate = -500
        return homeplanet


# EOF
