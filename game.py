#!/usr/bin/env python
#
# Script to simulate colonial expansion of the galaxy

import sys
import getopt
import time
import pygame

import ship
from galaxy import Galaxy

verbose = 0

CARGOSIZE = 1000000
MAXSHIPS = 50000

black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
purple = 255, 0, 255
white = 255, 255, 255

screensize = screenwidth, screenheight = 800, 800
galaxywidth = 800
galaxyheight = 800


##########################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])


##########################################################################
class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(screensize)
        self.galaxy = Galaxy(galaxywidth, galaxyheight)
        self.homeplanet = self.galaxy.findHomePlanet()
        self.shiplist = []
        self.year = 0

    ######################################################################
    def diaspora(self):
        for shp in self.shiplist[:]:
            if not shp.destination:
                shp.determine_destination(self.galaxy)
            if not shp.destination:
                self.shiplist.remove(shp)
                print "Ship %s gives up" % str(shp)
                continue

            if shp.location != shp.destination.location:
                shp.move()
            else:
                shp.unload()
                self.shiplist.remove(shp)
        for planet in self.galaxy.terrestrials:
            if planet.population > 1E9 and len(self.shiplist) < MAXSHIPS:
                for i in range(int(planet.population / 2E9)):
                    s = ship.Ship(planet)
                    s.destination = planet
                    s.load(CARGOSIZE)
                    self.shiplist.append(s)

    ######################################################################
    def printPopulatedGalaxy(self):
        for starsystem in self.galaxy.starsystems():
            for star in starsystem.stars():
                for planet in star.planets():
                    if planet.population > 0:
                        print "%s: %s (Dist %d)" % (str(planet), planet.population, planet.location.distance(self.homeplanet.location))

    ######################################################################
    def endOfYear(self):
        populated = 0
        popcap = 0
        totpop = 0
        for planet in self.galaxy.terrestrials:
            if planet.population > 0:
                totpop += planet.population
                populated += 1
                if planet.homeplanet:
                    planet.population += int(planet.population * 0.001)
                else:
                    planet.population += int(planet.population * 0.003)
                planet.population = min(planet.popcapacity, planet.population)
            if planet.popcapacity > 0:
                popcap += 1
        if populated == popcap:       # 100% colonised
            time.sleep(30)
        self.year += 1

    ######################################################################
    def drawText(self, surf, year, numships):
        populated = 0
        popcap = 0
        totpop = 0
        colpop = 0
        homepop = 0
        for planet in self.galaxy.terrestrials:
            if planet.population > 0:
                populated += 1
                totpop += planet.population
                if not planet.homeplanet:
                    colpop += planet.population
                else:
                    homepop = planet.population
            if planet.popcapacity > 0:
                popcap += 1
        font = pygame.font.Font(None, 20)
        toprint = [
            "Year: %d" % year,
            "Ships: %d" % numships,
            "Colonised: %d/%d" % (populated, popcap),
            "%0.2f%%" % (100.0 * populated / popcap),
            "Population: %0.4fB" % (totpop / 1E9),
            "Home %0.4fB" % (homepop / 1E9),
            "Colonists: %0.4fB" % (colpop / 1E9)
            ]
        text = font.render(" ".join(toprint), 1, white)
        textpos = text.get_rect(centerx=surf.get_width() / 2)
        surf.blit(text, textpos)

    ######################################################################
    def plot(self):
        self.screen.fill(black)
        for ss in self.galaxy.starsystems():
            ss.Plot(self.screen)
        for shp in self.shiplist:
            shp.Plot(self.screen)
        self.drawText(self.screen, self.year, len(self.shiplist))
        pygame.display.flip()
        pygame.time.wait(5)


##########################################################################
def main():
    game = Game()
    try:
        while(1):
            game.endOfYear()
            for i in range(12):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                game.diaspora()
                game.plot()
    except KeyboardInterrupt:
        game.printPopulatedGalaxy()

##########################################################################
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "v", [])
    except getopt.GetoptError, err:
        sys.stderr.write("Error: %s\n" % str(err))
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "-v":
            verbose = 1

    main()

# EOF
