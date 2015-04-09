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

CARGOSIZE = 1E6
MAXSHIPS = 5000

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
        self.numships = 0
        self.numslowships = 0
        self.abandoned = 0
        self.year = 0

    ######################################################################
    def diaspora(self):
        for shp in self.shiplist[:]:
            if shp.currplanet != shp.destination:
                shp.move()
            else:
                if shp.destination.plantype == 'gasgiant':
                    shp.destination = self.galaxy.determine_destination(shp)
                    if not shp.destination:
                        self.abandoned += shp.cargo
                        self.shiplist.remove(shp)
                else:
                    if not shp.destination.settledate:
                        shp.destination.settledate = self.year
                    shp.unload()
                    self.shiplist.remove(shp)

        for plnt in self.galaxy.terrestrials:
            if plnt.population >= 1E8:
                s = self.buildShip(plnt, speed=2)
                if s:
                    self.numships += 1

    ######################################################################
    def buildShip(self, plnt, speed, alloweddest=['terrestrial']):
        if len(self.shiplist) >= MAXSHIPS:
            return
        s = ship.Ship(startplanet=plnt)
        if plnt.maxdist < 5:
            return
        s.maxdist = plnt.maxdist + self.d6(3)
        s.destination = self.galaxy.determine_destination(s)
        if not s.destination:
            return
        if s.destination.plantype not in alloweddest:
            return
        s.load(CARGOSIZE)
        s.speed = speed
        self.shiplist.append(s)
        return s

    ######################################################################
    def printPopulatedGalaxy(self):
        for starsystem in self.galaxy.starsystems():
            for star in starsystem.stars():
                for plnt in star.planets():
                    if plnt.population > 0:
                        print "%s: %s (Dist %d)" % (str(plnt), plnt.population, plnt.location.distance(self.homeplanet.location))

    ######################################################################
    def endOfYear(self):
        populated = 0
        popcap = 0
        totpop = 0
        for plnt in self.galaxy.terrestrials:
            if plnt.population > 0:
                plnt.maxdist = int(
                    min((self.year - plnt.settledate) / 25, 50) +
                    min((self.year - plnt.settledate) / 50, 50) +
                    min((self.year - plnt.settledate) / 100, 50) +
                    (self.year - plnt.settledate) / 200)
                totpop += plnt.population
                populated += 1
                if plnt.homeplanet:
                    plnt.population += int(plnt.population * 0.001)
                else:
                    plnt.population += int(plnt.population * 0.003)
                plnt.population = min(plnt.popcapacity, plnt.population)
                if plnt.population >= 1E7 and self.d6() == 6:
                    s = self.buildShip(plnt, speed=1, alloweddest=['gasgiant'])
                    if s:
                        self.numslowships += 1
            if plnt.popcapacity > 0:
                popcap += 1
        # Simplistically refuel gas giants - should be 12 turns after ship arrives
        for plnt in self.galaxy.gasgiants:
            plnt.fueled = True
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
        for plnt in self.galaxy.terrestrials:
            if plnt.population > 0:
                populated += 1
                totpop += plnt.population
                if not plnt.homeplanet:
                    colpop += plnt.population
                else:
                    homepop = plnt.population
            if plnt.popcapacity > 0:
                popcap += 1
        font = pygame.font.Font(None, 20)
        toprint = [
            [
                "Year: %d" % self.year,
            ],
            [
                "Colonised: %d/%d" % (populated, popcap),
                "%0.2f%%" % (100.0 * populated / popcap),
            ],
            [
                "Pop: %s" % self.humanise(totpop),
                "Home %s" % self.humanise(homepop),
                "Col: %s" % self.humanise(colpop),
                "Dead: %s" % self.humanise(self.abandoned),
            ],
            [
                "Ships: %d" % len(self.shiplist),
                "Fast: %d" % self.numships,
                "Slow: %d" % self.numslowships,
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
