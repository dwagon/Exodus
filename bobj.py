#
import re
import sys
import random


###############################################################################
###############################################################################
###############################################################################
class BaseObj(object):
    ##########################################################################
    def dice(self, strng):
        if not strng:
            return 0
        reg = re.match("(?P<numdice>\d+)d(?P<modif>.*)", strng)
        if reg:
            numdice = int(reg.group("numdice"))
            val = self.d6(numdice)
            return eval("%d%s" % (val, reg.group("modif")))
        else:
            sys.stderr.write("No idea how to handle %s\n" % strng)
            sys.exit(0)

    ##########################################################################
    def d6(self, num=1):
        tot = 0
        for i in range(num):
            tot += int(random.random() * 6) + 1
        return tot

    ##########################################################################
    def humanise(self, num):
        """Convert a number to something human readable"""
        if num > 1e9:
            return "%0.2fB" % (num / 1e9)
        if num > 1e6:
            return "%0.2fM" % (num / 1e6)
        if num > 1e3:
            return "%0.2fK" % (num / 1e3)
        return "%d" % num


# EOF
