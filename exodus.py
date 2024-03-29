#!/usr/bin/env python
#
# Script to simulate colonial expansion of the galaxy

import sys
import getopt
import time
import pygame
from collections import defaultdict

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
        self.galaxy.homeplanet = self.homeplanet
        self.ships = defaultdict(list)
        self.liners = 0
        self.colonisers = 0
        self.abandoned = 0
        self.year = 0

    ######################################################################
    def diaspora(self):
        for shptype in self.ships:
            for shp in self.ships[shptype][:]:
                if shp.currplanet != shp.destination:
                    shp.move()
                else:
                    if shp.destination.plantype == "gasgiant":
                        dest = shp.determine_destination()
                        if not dest:
                            self.abandoned += shp.cargo
                            self.ships[shptype].remove(shp)
                    else:
                        if not shp.destination.settledate:
                            shp.destination.settledate = self.year
                        shp.unload()
                        self.ships[shptype].remove(shp)

        # Any populous planet can spin off liners
        for plnt in self.galaxy.terrestrials:
            self.buildShip(plnt, Liner)

    ######################################################################
    def buildShip(self, plnt, shipklass):
        sk = shipklass.__name__
        if len(self.ships[sk]) >= maxships[sk]:
            return
        s = shipklass(startplanet=plnt, galaxy=self.galaxy)
        if not s.doSpawn():
            return
        dest = s.determine_destination()
        if not dest:
            return
        s.load(s.cargosize)
        self.ships[sk].append(s)
        plnt.launches[sk] += 1
        return s

    ######################################################################
    def endOfYear(self):
        populated = 0
        popcap = 0
        totpop = 0
        for plnt in self.galaxy.terrestrials:
            if plnt.population > 0:
                plnt.maxdist = int(
                    min((self.year - plnt.settledate) / 20, 50)
                    + min((self.year - plnt.settledate) / 40, 50)
                    + min((self.year - plnt.settledate) / 80, 50)
                    + min((plnt.population / 1e9), 20)
                    + (self.year - plnt.settledate) / 200
                )
                totpop += plnt.population
                populated += 1
                if plnt.homeplanet:
                    plnt.population += int(plnt.population * 0.001)
                else:
                    plnt.population += int(plnt.population * 0.003)
                plnt.population = min(plnt.popcapacity, plnt.population)
                # Very populous planets can generate colonisers
                self.buildShip(plnt, Coloniser)
            if plnt.popcapacity > 0:
                popcap += 1
        if populated == popcap:  # 100% colonised
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
                "Liners: %d" % len(self.ships["Liner"]),
                "Colonisers: %d" % len(self.ships["Coloniser"]),
            ],
        ]
        count = 1
        for tp in toprint:
            text = font.render(" ".join(tp), 1, white)
            textpos = text.get_rect(centerx=surf.get_width() / 2, centery=count * 20)
            surf.blit(text, textpos)
            count += 1

        if stsys:
            for s in stsys.stars():
                count = 5
                st = "Star %s" % s.stardesc
                text = font.render(st, 1, white)
                textpos = text.get_rect(left=0, centery=count * 20)
                surf.blit(text, textpos)
                count += 1
                for p in s.planets():
                    st = "Orbit %d %s " % (p.orbit, p.plantype)
                    if p.popcapacity:
                        st += "Pop: %s/%s (%s) %s" % (
                            self.humanise(p.population),
                            self.humanise(p.popcapacity),
                            p.settledate,
                            p.launchstr(),
                        )
                    text = font.render(st, 1, white)
                    textpos = text.get_rect(left=0, centery=count * 20)
                    count += 1
                    surf.blit(text, textpos)
                    if p.maxdist > 5:
                        pygame.draw.circle(surf, white, abs(p.location), p.maxdist, 1)

    ######################################################################
    def plot(self, stsys):
        self.screen.fill(black)
        for ss in self.galaxy.starsystems():
            ss.Plot(self.screen)
        for shptyp in self.ships:
            for shp in self.ships[shptyp]:
                shp.Plot(self.screen)
        self.drawText(stsys)
        pygame.display.flip()


##########################################################################
def main():
    game = Game()
    stsys = None
    try:
        while 1:
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
    except getopt.GetoptError as err:
        sys.stderr.write("Error: %s\n" % str(err))
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "-v":
            verbose = 1

    main()

# EOF
