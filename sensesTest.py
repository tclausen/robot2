#!/usr/bin/python

import sys
import time

from Senses import *

s = Senses()

s.showTrackbars(s.iLower, s.iUpper)

try:
    while True:
        (f, t) = Senses.getFrame()
        s.findArm(f, 1, 20)
        Senses.showFrame(f)
                        
except KeyboardInterrupt:
    # quit
    Senses.close()
    sys.exit()
