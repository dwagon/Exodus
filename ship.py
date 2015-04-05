import pygame
import random
import sys

import coord
from bobj import BaseObj

CARGOSIZE = 100000000
mode = 1

purple = 255, 0, 255
white = 255, 255, 255


##########################################################################
class Ship(BaseObj):
    def __init__(self, startplanet=None, name=None):
        self.currplanet = None
        if startplanet:
            self.location, self.orbit = startplanet.location, startplanet.orbit
        else:
            self.location = coord.Coord(0, 0, 0)
            self.orbit = 0
        if not name:
            self.name = self.GenerateName()
        else:
            self.name = name
        self.speed = 2
        self.cargo = 0
        self.loaded = 0
        self.destination = None

    ##########################################################################
    def Plot(self, surf):
        color = None
        if self.loaded:
            color = purple
        else:
            color = white

        if self.destination:
            pygame.draw.line(
                surf, color, abs(self.location), abs(self.destination.location), 1)
        pygame.draw.circle(surf, color, abs(self.location), 2, 0)

    ##########################################################################
    def GenerateName(self):
        return "ship"
        f = open('/usr/share/dict/words')
        output = f.readlines()
        f.close()
        numchoices = len(output)
        pos = int(random.random() * numchoices)
        return output[pos].strip().capitalize()

    ##########################################################################
    def __repr__(self):
        if self.destination:
            return "<Ship %s at %s going to %s cargo: %s>" % (self.name, self.location, self.destination.location, self.cargo)
        else:
            return "<Ship %s at %s going nowhere cargo: %s>" % (self.name, self.location, self.cargo)

    ##########################################################################
    def has_destination(self):
        if self.destination:
            return 1
        return 0

    ##########################################################################
    def determine_destination(self, galaxy):
        closestbest = 0.0
        best = None
        for planet in galaxy.terrestrials:
            if self.loaded:
                # Emphasise uncolonised planets
                if planet.homeplanet:
                    continue
                if self.currplanet:
                    if planet.population > self.currplanet.population:
                        continue
                if mode == 0:
                    if planet.population != 0:
                        continue
                    else:
                        desire = planet.popcapacity / 1000
                elif mode == 1:
                    # KORG try desire relation to available capacity
                    desire = planet.popcapacity / 1000 - (planet.population * 100000)
                    desire = 100. * ((planet.popcapacity - planet.population) /
                                     (1.0 * planet.popcapacity)) ** 5 * planet.popcapacity
                    if desire < 0.0:
                        desire = 0.0
                else:
                    sys.stderr.write("Unknown mode %d\n" % mode)
                    sys.exit(1)
            else:
                desire = planet.population
            distance = self.location.distance(planet.location)
            if distance < 4:
                continue
            distmod = distance ** 2.0       # Emphasise closeness
            pull = float(desire) / distmod * (1.0 - random.random() / 5.0)
            if pull > closestbest:
                best = planet
                closestbest = pull
            if not best:
                sys.stderr.write("No better location than here for %s\n" % repr(self))
                return self.location
            self.destination = best

    ##########################################################################
    def move(self):
        moved = 0
        goes = 0
        self.currplanet = None
        x, y, z = self.location.coords()
        destx, desty, destz = self.destination.location.coords()
        while moved < self.speed:
            if x == destx and y == desty and z == destz:
                break
            goes += 1
            if goes > self.speed * 200:  # Hey we got lost
                print "Got lost (%s,%s,%s)->(%s,%s,%s)" % (x, y, z, destx, desty, destz)
                break
            a = self.d6()
            if a in (1, 2):
                if x < destx:
                    x += 1
                    moved += 1
                elif x > destx:
                    x -= 1
                    moved += 1
            elif a in (3, 4):
                if y < desty:
                    y += 1
                    moved += 1
                elif y > desty:
                    y -= 1
                    moved += 1
            else:
                if z < destz:
                    z += 1
                    moved += 1
                elif z > destz:
                    z -= 1
                    moved += 1
        self.location = coord.Coord(x, y, z)

    ##########################################################################
    def load(self):
        if self.destination.population < CARGOSIZE * 2:
            return
        self.loaded = 1
        self.cargo = CARGOSIZE
        self.destination.population -= self.cargo
        self.currplanet = self.destination
        self.destination = None

    ##########################################################################
    def unload(self):
        self.loaded = 0
        self.destination.population += self.cargo
        self.loaded = 0
        self.cargo = 0
        self.currplanet = self.destination
        self.destination = None

    ##########################################################################
    def destination(self, loc=None):
        if not loc:
            return self.destination
        else:
            self.destination = loc

# EOF
