import pygame
from ship import Ship


##############################################################################
##############################################################################
class Coloniser(Ship):
    ##########################################################################
    def __init__(self, startplanet, galaxy):
        Ship.__init__(self, startplanet, galaxy)
        self.speed = 1
        self.color = 255, 255, 255  # White
        self.maxdist = startplanet.maxdist + self.d6(2)
        self.cargosize = 1e4
        self.visited = [startplanet.location]

    ##########################################################################
    def doSpawn(self):
        plnt = self.startplanet
        spawn = False
        if plnt.population >= 1e9 and self.d6(2) > 8:
            spawn = True
        elif plnt.population >= 1e8 and self.d6(2) > 10:
            spawn = True
        elif plnt.population >= 1e7 and self.d6(2) == 12:
            spawn = True
        else:
            return False
        if not spawn:
            return False
        if self.nearestEmptyTerrestrial() > self.maxdist * 3:
            return False
        return True

    ##########################################################################
    def Plot(self, surf):
        points = []
        for i in self.visited:
            points.append((i.x, i.y))
        points.append((self.location.x, self.location.y))

        pygame.draw.lines(surf, self.color, False, points, 1)
        pygame.draw.circle(surf, self.color, abs(self.location), 2, 0)

    ##########################################################################
    def determine_destination(self):
        """Colonisers can't go to populated planets"""
        closestbest = 0.0
        best = None
        for plnt in self.galaxy.terrestrials:
            if plnt.location in self.visited:
                continue
            if plnt == self.currplanet:
                continue
            if plnt.homeplanet:
                continue
            if plnt.population:
                continue

            distance = self.location.distance(plnt.location)
            if distance > self.maxdist:
                continue

            try:
                pull = 1 / distance
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
        homedistance = self.location.distance(self.galaxy.homeplanet.location)

        for plnt in self.galaxy.gasgiants:
            if plnt.location in self.visited:
                continue
            distance = self.location.distance(plnt.location)
            if distance > self.maxdist:
                continue
            # Move away from the home planet
            newdist = plnt.location.distance(self.galaxy.homeplanet.location)
            if newdist < homedistance:
                continue
            if distance > furthest:
                furthest = distance
                best = plnt
        if best:
            self.visited.append(best.location)
        return best


# EOF
