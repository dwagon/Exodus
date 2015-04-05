import pygame
import random

import coord
from bobj import BaseObj

purple = 255, 0, 255
white = 255, 255, 255


##########################################################################
class Ship(BaseObj):
    def __init__(self, startplanet=None, name=None):
        self.currplanet = None
        if startplanet:
            self.location, self.orbit = startplanet.location, startplanet.orbit
        else:
            self.location = coord.Coord(0, 0)
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
            return True
        return False

    ##########################################################################
    def determine_destination(self, galaxy):
        closestbest = 0.0
        best = None
        for planet in galaxy.terrestrials:
            if planet == self.currplanet:
                continue
            if planet.homeplanet:
                continue
            if planet.population > self.currplanet.population:
                continue

            desire = 100 - int(100.0 * planet.population / planet.popcapacity)
            if planet.population == 0:
                desire += 100
            distance = self.location.distance(planet.location)
            if distance < 1.0:
                continue

            pull = float(desire) / distance
            pull += self.d6()
            if pull > closestbest:
                best = planet
                closestbest = pull
        self.destination = best

    ##########################################################################
    def move(self):
        self.currplanet = None
        if self.location.distance(self.destination.location) < self.speed:
            self.location = self.destination.location
        else:
            direct = self.location.angle(self.destination.location)
            self.location = self.location.vector(direct, self.speed)

    ##########################################################################
    def load(self, cargo):
        if self.destination.population < cargo * 2:
            return
        self.loaded = 1
        self.cargo = cargo
        self.destination.population -= self.cargo
        self.currplanet = self.destination
        self.destination = None

    ##########################################################################
    def unload(self):
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
