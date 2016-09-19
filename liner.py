from ship import Ship


##############################################################################
##############################################################################
class Liner(Ship):
    ##########################################################################
    def __init__(self, startplanet, galaxy):
        Ship.__init__(self, startplanet, galaxy)
        self.speed = 3
        self.color = 255, 0, 255    # Purple
        self.maxdist = startplanet.maxdist + self.d6()
        self.cargosize = 1E6 * self.d6()

    ##########################################################################
    def doSpawn(self):
        plnt = self.startplanet
        if plnt.population / plnt.popcapacity < 0.5:
            return False
        if (plnt.population >= 1E9 and self.d6() == 6) or (plnt.population >= 1E8 and self.d6(2) > 10) or (plnt.population >= 1E7 and self.d6(2) == 12):
            return True
        return False

    ##########################################################################
    def determine_destination(self):
        """ Liners can only go to colonised planets """
        closestbest = 0.0
        best = None
        for plnt in self.galaxy.terrestrials:
            if plnt == self.currplanet:
                continue
            if plnt.homeplanet:
                continue
            if plnt.settledate and plnt.settledate < self.currplanet.settledate:
                continue
            if plnt.population > self.currplanet.population:
                continue
            if plnt.population == 0:
                continue

            desire = 100 - int(100.0 * plnt.population / plnt.popcapacity)
            if desire < 5:     # Don't colonise full planets
                continue
            distance = self.location.distance(plnt.location)
            if distance > self.maxdist:
                continue

            try:
                pull = float(desire) / distance
            except ZeroDivisionError:
                pull = 1
            pull += self.d6()
            if pull > closestbest:
                best = plnt
                closestbest = pull
        self.destination = best
        return best

# EOF
