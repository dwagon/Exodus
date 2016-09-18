import pygame

from bobj import BaseObj


##########################################################################
class Ship(BaseObj):
    def __init__(self, startplanet, galaxy):
        self.currplanet = None
        self.galaxy = galaxy
        self.location, self.orbit = startplanet.location, startplanet.orbit
        self.currplanet = startplanet
        self.cargo = 0
        self.loaded = False
        self.destination = None
        self.visited = set([startplanet.location])

    ##########################################################################
    def Plot(self, surf):
        pygame.draw.circle(surf, self.color, abs(self.location), 2, 0)

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
