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
            self.currplanet = startplanet
        else:
            self.location = coord.Coord(0, 0)
            self.orbit = 0
        if not name:
            self.name = self.GenerateName()
        else:
            self.name = name
        self.speed = 1
        self.refueled = False
        self.maxdist = 100
        self.cargo = 0
        self.loaded = False
        self.destination = None
        self.visited = set([startplanet.location])

    ##########################################################################
    def Plot(self, surf):
        color = None
        if self.refueled:
            color = white
        else:
            color = purple

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
    def move(self):
        if self.location.distance(self.destination.location) < self.speed:
            self.location = self.destination.location
            self.currplanet = self.destination
        else:
            direct = self.location.angle(self.destination.location)
            self.location = self.location.vector(direct, self.speed)
            self.currplanet = None

    ##########################################################################
    def load(self, cargo):
        if self.currplanet.population < cargo * 2:
            return
        self.loaded = True
        self.cargo = cargo
        self.currplanet.population -= self.cargo

    ##########################################################################
    def unload(self):
        self.currplanet.population += self.cargo
        self.loaded = False
        self.cargo = 0
        self.destination = None

    ##########################################################################
    def destination(self, loc=None):
        if not loc:
            return self.destination
        else:
            self.destination = loc

# EOF
