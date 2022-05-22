import sys
from bobj import BaseObj
from collections import defaultdict


##########################################################################
class Planet(BaseObj):
    def __init__(self, plantype, loc, orbit, atmosphere="normal"):
        self.plantype = plantype
        self.location = loc
        self.maxdist = 0
        self.maxdist_ticks = None
        self.orbit = orbit
        self.size = 0
        self.settledate = 0
        self.density = 0
        self.gravity = 0
        self.homeplanet = False
        self.population = 0
        self.popcapacity = 0
        self.launches = defaultdict(int)
        if plantype == "terrestrial":
            self.genTerrestrial()
        elif plantype == "gasgiant":
            self.genGasgiant()
        elif plantype == "asteroid":
            self.genAsteroid()
        elif plantype == "rockball":
            self.genRockball()
        elif plantype == "browndwarf":
            self.genBrowndwarf()
        elif plantype == "greenhouse":
            self.genGreenhouse()
        else:
            sys.stderr.write("Unhandled planettype %s\n" % plantype)
        self.gravity = self.size * self.density * 0.0000228

    ##########################################################################
    def launchstr(self):
        out = []
        for k, v in self.launches.items():
            out.append("%s=%d" % (k, v))
        return "; ".join(out)

    ##########################################################################
    def Plot(self, surf):
        print("Plot(planet)")
        pass

    ##########################################################################
    def genGreenhouse(self):
        pass

    ##########################################################################
    def genBrowndwarf(self):
        pass

    ##########################################################################
    def genRockball(self):
        pass

    ##########################################################################
    def genAsteroid(self):
        pass

    ##########################################################################
    def genGasgiant(self):
        self.size = (self.d6(2) + 2) * 10000
        self.density = (self.d6(3) / 10.0) + 0.5

    ##########################################################################
    def genTerrestrial(self):
        self.size = self.d6(2) * 1000
        self.density = self.d6(3) / 10.0 + self.d6()
        x = self.d6(2)
        if x in (2, 3, 4):
            self.genRockball()
            self.popcapacity = 1e6
        elif x == 5:
            self.popcapacity = 1e9
            self.genGreenhouse()
        elif x in (6, 7):
            # Earthlike
            self.popcapacity = 1e10
        elif x in (8, 9):
            # Desert
            self.popcapacity = 1e8
        elif x == 10:
            # Hostile
            self.popcapacity = 1e7
        elif x == 11:
            # Icy rockball
            self.popcapacity = 1e6
        else:
            # Iceball
            self.popcapacity = 1e6

    ##########################################################################
    def __repr__(self):
        planstr = ""
        if self.population > 0:
            planstr = "Population: %s" % self.population
        else:
            planstr = "Empty"
        return "<Planet %s: %s, Orbit %s %s>" % (
            self.plantype,
            repr(self.location),
            self.orbit,
            planstr,
        )


# EOF
