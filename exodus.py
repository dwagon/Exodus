#!/usr/bin/env python
#
# Script to simulate colonial expansion of the galaxy

import sys
import getopt
import time
import pygame

import ship
from galaxy import Galaxy
import bobj

verbose = 0

CARGOSIZE = 1000000
MAXSHIPS = 500

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
class Game(bobj.BaseObj):
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
            if shp.currplanet != shp.destination:
                shp.move()
            else:
                if not shp.destination.settledate:
                    shp.destination.settledate = self.year
                shp.unload()
                self.shiplist.remove(shp)

        for planet in self.galaxy.terrestrials:
            if planet.population > 1E8 and len(self.shiplist) < MAXSHIPS:
                for i in range(1):
                    s = ship.Ship(startplanet=planet)
                    planet.maxdist = \
                        min((self.year - planet.settledate) / 20, 20) + \
                        min((self.year - planet.settledate) / 50, 50) + \
                        (self.year - planet.settledate) / 200
                    if planet.maxdist > 5:
                        s.maxdist = planet.maxdist + self.d6(3)
                        s.determine_destination(self.galaxy)
                        if not s.destination:
                            continue
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
    def drawText(self, stsys):
        surf = self.screen
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
            [
                "Year: %d" % self.year,
                "Ships: %d" % len(self.shiplist),
            ],
            [
                "Colonised: %d/%d" % (populated, popcap),
                "%0.2f%%" % (100.0 * populated / popcap),
            ],
            [
                "Population: %s" % self.humanise(totpop),
                "Home %s" % self.humanise(homepop),
                "Colonists: %s" % self.humanise(colpop)
            ]
        ]
        count = 1
        for tp in toprint:
            text = font.render(" ".join(tp), 1, white)
            textpos = text.get_rect(centerx=surf.get_width() / 2, centery=count*20)
            surf.blit(text, textpos)
            count += 1

        if stsys:
            for s in stsys.stars():
                count = 5
                st = "Star %s" % s.stardesc
                text = font.render(st, 1, white)
                textpos = text.get_rect(left=0, centery=count*20)
                surf.blit(text, textpos)
                count += 1
                for p in s.planets():
                    st = "Orbit %d %s " % (p.orbit, p.plantype)
                    if p.popcapacity:
                        st += "Pop: %s/%s " % (self.humanise(p.population), self.humanise(p.popcapacity))
                    text = font.render(st, 1, white)
                    textpos = text.get_rect(left=0, centery=count*20)
                    count += 1
                    surf.blit(text, textpos)
                    if p.maxdist > 5:
                        pygame.draw.circle(surf, white, abs(p.location), p.maxdist+18, 1)

    ######################################################################
    def plot(self, stsys):
        self.screen.fill(black)
        for ss in self.galaxy.starsystems():
            ss.Plot(self.screen)
        for shp in self.shiplist:
            shp.Plot(self.screen)
        self.drawText(stsys)
        pygame.display.flip()
        # pygame.time.wait(5)


##########################################################################
def main():
    game = Game()
    stsys = None
    starttick = pygame.time.get_ticks()
    try:
        while(1):
            game.endOfYear()
            for i in range(12):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        stsys = game.galaxy.click(event.pos)
                        starttick = pygame.time.get_ticks()
                game.diaspora()
                if pygame.time.get_ticks() - starttick > 5000:
                    stsys = None
                game.plot(stsys)
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