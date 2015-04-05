#!/usr/bin/env python
#
# Star
import bobj
import sys
from planet import Planet


##########################################################################
class Star(bobj.BaseObj):
    def __init__(self, loc):
        bits = self.genStarClass()
        self.location = loc
        self.startype = bits[0]
        self.stardesc = bits[1]
        self.starsize = bits[2]
        self.orbits = []
        self.genOrbits(self.startype, self.starsize)

    ##########################################################################
    def Plot(self, surf):
        print "Plot(star)"

    ##########################################################################
    def planets(self):
        return [orbit for orbit in self.orbits if orbit is not None]

    ##########################################################################
    def __repr__(self):
        return "<Star: %s %s %s>" % (self.startype, self.starsize, self.stardesc)

    ##########################################################################
    def genOrbits(self, startype, starsize):
        bits = self.getOrbitData(startype, starsize)
        if not bits:
            return
        size, stellmass, bzonestart, bzoneend, limit, stellrad, plan, orbs, life = bits
        if self.d6(3) >= plan:     # No planets
            return
        for i in range(self.dice(orbs)):
            radius = self.genOrbitRadius(startype, starsize, stellrad, i)
            if radius < bzonestart:   # Orbits before the biozone
                x = self.d6(2)
                if 2 <= x <= 4:
                    self.orbits.append(None)
                elif 5 <= x <= 6:
                    self.orbits.append(Planet('greenhouse', self.location, i))
                elif 7 <= x <= 9:
                    self.orbits.append(Planet('rockball', self.location, i))
                elif 10 <= x <= 11:
                    self.orbits.append(Planet('asteroid', self.location, i))
                else:
                    if i == 0:
                        self.orbits.append(None)
                    else:
                        self.orbits.append(Planet('browndwarf', self.location, i))
            elif radius > bzoneend:   # Orbits after the biozone
                x = self.d6()
                if radius > 10 * bzoneend:
                    x += 1
                if x == 1:
                    self.orbits.append(Planet('terrestrial', self.location, i))
                elif x == 2:
                    self.orbits.append(Planet('asteroid', self.location, i))
                elif x == 2:
                    self.orbits.append(None)
                elif 4 <= x <= 6:
                    self.orbits.append(Planet('gasgiant', self.location, i))
                elif x == 7:
                    self.orbits.append(
                        Planet('terrestrial', self.location, i, atmosphere='trace'))
            else:   # Orbits within the biozone
                x = self.d6(2)
                if x in (2, 3):
                    self.orbits.append(None)
                elif 4 <= x <= 8:
                    self.orbits.append(Planet('terrestrial', self.location, i))
                elif x in (9, 10):
                    self.orbits.append(Planet('asteroid', self.location, i))
                elif x == 11:
                    self.orbits.append(Planet('gasgiant', self.location, i))
                else:
                    self.orbits.append(Planet('browndwarf', self.location, i))

    ##########################################################################
    def genOrbitRadius(self, startype, starsize, stellradius, orbitnum):
        inner = self.d6() * 0.1
        if orbitnum == 0:
            if inner < stellradius:
                return None
            else:
                return inner
        bode = self.genBodeConstant(startype, starsize)
        return inner + (2 ** orbitnum) * bode

    ##########################################################################
    def genBodeConstant(self, startype, starsize):
        if startype == 'M' and starsize == 'VI':
            bode = 0.2
        else:
            x = self.d6()
            if x in (1, 2):
                bode = 0.3
            elif x in (3, 4):
                bode = 0.35
            else:
                bode = 0.4
        return bode

    ##########################################################################
    def getOrbitData(self, startype, starsize):
        """
        size, stellar mass, biozone start, biozone end, inner limit, stellar radius,
        planets on, #orbits, life roll
        """
        orbitData = {
            'O': [
                ('Ia', 70, 790, 1190, 16, 0.2, 0, '', -12),
                ('Ib', 60, 630, 950, 13, 0.1, 0, '', -12),
                ('V', 50, 500, 750, 10, 0.0, 0, '', -9),
            ],
            'B': [
                ('Ia', 50, 500, 750, 10, 0.2, 0, '', -10),
                ('V', 10, 30, 45, 0.6, 0, 4, '3d', -9),
            ],
            'A': [
                ('Ia', 30, 200, 300, 4.0, 0.6, 3, '3d+3', -10),
                ('III', 6, 5, 7.5, 0, 0, 3, '3d+1', -10),
                ('V', 3.0, 3.1, 4.7, 0, 0, 5, '3d-1', -9),
            ],
            'F': [
                ('Ia', 15, 200, 300, 4.0, 0.8, 4, '3d+3', -10),
                ('V', 1.9, 1.6, 2.4, 0, 0, 13, '3d-1', -8),
            ],
            'G': [
                ('Ia', 12, 160, 240, 3.1, 1.4, 6, '3d+3', -10),
                ('V', 1.1, 0.8, 1.2, 0, 0, 16, '3d-2', 0),
                ('VI', 0.8, 0.5, 0.8, 0, 0, 16, '2d+1', 1),
            ],
            'K': [
                ('Ia', 15, 125, 190, 2.5, 3.0, 10, '3d+2', -10),
                ('V', 0.9, 0.5, 0.6, 0, 0, 16, '3d-2', 0),
                ('VI', 0.5, 0.2, 0.3, 0, 0, 16, '2d+1', 1),
            ],
            'M': [
                ('Ia', 20, 100, 150, 2, 7, 16, '3d', -10),
                ('Ib', 16, 50, 76, 1, 4.2, 16, '3d', -10),
                ('II', 8, 16, 24, 0.3, 1.1, 16, '3d', -9),
                ('III', 4, 5, 7.5, 0.1, 0.3, 16, '3d', -6),
                ('V', 0.3, 0.1, 0.2, 0, 0, 16, '3d-2', +1),
                ('VI', 0.2, 0.1, 0.1, 0, 0, 16, '2d+2', +2),
            ],
            'D': [],
        }
        if startype == 'D':   # Ignore for now
            return None

        if startype not in orbitData:
            sys.stderr.write("No orbitData for type %s\n" % startype)
            return None
        for i in orbitData[startype]:
            if i[0] == starsize:
                return i
        sys.stderr.write("No orbitData for type %s size %s\n" % (startype, starsize))
        return None

    ##########################################################################
    def genGiantType(self, desc, size):
        x = self.d6(2)
        if x == 2:
            return ("O", "Blue %s" % desc, size)
        elif x == 3:
            return ("M", "Red %s" % desc, size)
        elif x in (4, 5):
            return ("B", "Blue-White %s" % desc, size)
        elif 6 <= x <= 9:
            return ("K", "Orange %s" % desc, size)
        else:
            return ("A", "White %s" % desc, size)

    ##########################################################################
    def genStarClass(self):
        x = self.d6(3)
        if 3 <= x <= 5:  # White Dwarf
            return ("D", "White Dwarf", "")
        elif x == 6:  # Subdwarf
            y = self.d6()
            if y == 1:
                return ("G", "Yellow Subdwarf", "VI")
            elif y == 2:
                return ("K", "Orange Subdwarf", "VI")
            else:
                return ("M", "Red Subdwarf", "VI")
        elif 7 <= x <= 17:  # Main sequence
            y = self.d6(3)
            if y == 3:
                return ("O", "Blue", "V")
            elif y == 4:
                return ("B", "Blue-White", "V")
            elif y == 5:
                return ("A", "White", "V")
            elif y == 6:
                return ("F", "Yellow-White", "V")
            elif y == 7:
                return ("G", "Yellow", "V")
            elif y == 8:
                return ("K", "Orange", "V")
            else:
                return ("M", "Red", "V")
        else:       # Giant star
            y = self.d6(3)
            if y == 3:
                z = self.self.d6(1)
                if 1 <= z <= 2:
                    return self.genGiantType("SuperGiant", "Ia")
                else:
                    return self.genGiantType("SuperGiant", "Ib")
            elif y == 4:
                return self.genGiantType("Large Giant", "II")
            elif 5 <= y <= 12:
                return self.genGiantType("Giant", "III")
            else:
                return self.genGiantType("Subgiant", "IV")

# EOF
