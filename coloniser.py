from ship import Ship


##############################################################################
##############################################################################
class Coloniser(Ship):
    ##########################################################################
    def __init__(self, startplanet, galaxy):
        Ship.__init__(self, startplanet, galaxy)
        self.speed = 1
        self.color = 255, 255, 255  # White
        self.maxdist = startplanet.maxdist + self.d6(10)
        self.cargosize = 1E4

    ##########################################################################
    def determine_destination(self):
        """ Colonisers can't go to populated planets """
        closestbest = 0.0
        best = None
        for plnt in self.galaxy.terrestrials:
            if plnt in self.visited:
                continue
            if plnt == self.currplanet:
                continue
            if plnt.homeplanet:
                continue
            if plnt.population:
                continue
            desire = 100

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
        if not best:
            best = self.furthestFuel()
        self.destination = best
        return best

    ##########################################################################
    def furthestFuel(self):
        furthest = 0.0
        best = None

        # Occassionally you just can't refuel
        if self.d6() == 6:
            return None

        for plnt in self.galaxy.gasgiants:
            if plnt.location in self.visited:
                continue
            distance = self.location.distance(plnt.location)
            if distance > self.maxdist:
                continue
            if distance > furthest:
                furthest = distance
                best = plnt
        if best:
            self.visited.add(best.location)
        return best

# EOF
