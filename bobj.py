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
        reg = re.match('(?P<numdice>\d+)d(?P<modif>.*)', strng)
        if reg:
            numdice = int(reg.group('numdice'))
            val = self.d6(numdice)
            return eval("%d%s" % (val, reg.group('modif')))
        else:
            sys.stderr.write("No idea how to handle %s\n" % strng)
            sys.exit(0)

    ##########################################################################
    def d6(self, num=1):
        tot = 0
        for i in range(num):
            tot += int(random.random() * 6) + 1
        return tot


# EOF
