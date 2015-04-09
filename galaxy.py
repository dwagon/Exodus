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
        print "%d terrestrials" % len(self.terrestrials)
        self.gasgiants = self.getGasGiants()
        print "%d gasgiants" % len(self.gasgiants)

    ##########################################################################
    def click(self, pos):
        for x in (0, -1, 1, -2, 2, -3, 3):
            for y in (0, -1, 1, -2, 2, -3, 3):
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
            if planet.plantype == 'gasgiant':
                tmp.append(planet)
        return tmp

    ##########################################################################
    def determine_destination(self, shp):
        closestbest = 0.0
        best = None
        for plnt in self.terrestrials:
            if plnt in shp.visited:
                continue
            if plnt == shp.currplanet:
                continue
            if plnt.homeplanet:
                continue
            if plnt.population > shp.currplanet.population:
                continue

            desire = 100 - int(100.0 * plnt.population / plnt.popcapacity)
            if desire < 5:     # Don't colonise full planets
                continue
            if plnt.population == 0:  # Emphasise empty planets
                desire += 100
            distance = shp.location.distance(plnt.location)
            if distance > shp.maxdist:
                continue

            try:
                pull = float(desire) / distance
            except ZeroDivisionError:
                pull = 1
            pull += self.d6()
            if pull > closestbest:
                best = plnt
                closestbest = pull
        if not best:
            best = self.furthestFuel(shp)
        return best

    ##########################################################################
    def furthestFuel(self, shp):
        furthest = 0.0
        best = None
        for plnt in self.gasgiants:
            if not plnt.fueled:
                continue
            if plnt.location in shp.visited:
                continue
            distance = shp.location.distance(plnt.location)
            if distance > shp.maxdist:
                continue
            if distance > furthest:
                furthest = distance
                best = plnt
        if best:
            best.fueled = False
            shp.visited.add(best.location)
            shp.refueled = True
        return best

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
