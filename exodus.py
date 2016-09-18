#!/usr/bin/env python
#
# Script to simulate colonial expansion of the galaxy

import sys
import getopt
import time
import pygame

from coloniser import Coloniser
from liner import Liner
from galaxy import Galaxy
from config import galaxywidth, galaxyheight, screensize, maxships
import bobj

black = 0, 0, 0
white = 255, 255, 255


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
        self.liners = 0
        self.colonisers = 0
        self.abandoned = 0
        self.year = 0

    ######################################################################
    def diaspora(self):
        for shp in self.shiplist[:]:
            if shp.currplanet != shp.destination:
                shp.move()
            else:
                if shp.destination.plantype == 'gasgiant':
                    dest = shp.determine_destination()
                    if not dest:
                        self.abandoned += shp.cargo
                        self.shiplist.remove(shp)
                else:
                    if not shp.destination.settledate:
                        shp.destination.settledate = self.year
                    shp.unload()
                    self.shiplist.remove(shp)

        # Any populous planet can spin off liners
        for plnt in self.galaxy.terrestrials:
            if (plnt.population >= 1E9 and self.d6() == 6) or (plnt.population >= 1E8 and self.d6(2) > 10) or (plnt.population >= 1E7 and self.d6(2) == 12):
                self.buildShip(plnt, Liner)

    ######################################################################
    def buildShip(self, plnt, shipklass):
        if len(self.shiplist) >= maxships[shipklass.__name__]:
            return
        s = shipklass(startplanet=plnt, galaxy=self.galaxy)
        dest = s.determine_destination()
        if not dest:
            return
        s.load(s.cargosize)
        self.shiplist.append(s)
        plnt.launches[shipklass.__name__] += 1
        return s

    ######################################################################
    def endOfYear(self):
        populated = 0
        popcap = 0
        totpop = 0
        for plnt in self.galaxy.terrestrials:
            if plnt.population > 0:
                plnt.maxdist = int(
                    min((self.year - plnt.settledate) / 20, 50) +
                    min((self.year - plnt.settledate) / 40, 50) +
                    min((self.year - plnt.settledate) / 80, 50) +
                    min((plnt.population / 1E9), 20) +
                    (self.year - plnt.settledate) / 200)
                totpop += plnt.population
                populated += 1
                if plnt.homeplanet:
                    plnt.population += int(plnt.population * 0.001)
                else:
                    plnt.population += int(plnt.population * 0.003)
                plnt.population = min(plnt.popcapacity, plnt.population)
                # Very populous planets can generate colonisers
                if plnt.population >= 1E9 and self.d6(2) > 8:
                    self.buildShip(plnt, Coloniser)
                elif plnt.population >= 1E8 and self.d6(2) > 10:
                    self.buildShip(plnt, Coloniser)
                elif plnt.population >= 1E7 and self.d6(2) == 12:
                    self.buildShip(plnt, Coloniser)
            if plnt.popcapacity > 0:
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
                        st += "Pop: %s/%s (%s) %s" % (self.humanise(p.population), self.humanise(p.popcapacity), p.settledate, p.launchstr())
                    text = font.render(st, 1, white)
                    textpos = text.get_rect(left=0, centery=count*20)
                    count += 1
                    surf.blit(text, textpos)
                    if p.maxdist > 5:
                        pygame.draw.circle(surf, white, abs(p.location), p.maxdist, 1)

    ######################################################################
    def plot(self, stsys):
        self.screen.fill(black)
        for ss in self.galaxy.starsystems():
            ss.Plot(self.screen)
        for shp in self.shiplist:
            shp.Plot(self.screen)
        self.drawText(stsys)
        pygame.display.flip()


##########################################################################
def main():
    game = Game()
    stsys = None
    try:
        while(1):
            game.endOfYear()
            for i in range(12):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        stsys = game.galaxy.click(event.pos)
                game.diaspora()
                game.plot(stsys)
    except KeyboardInterrupt:
        return

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
