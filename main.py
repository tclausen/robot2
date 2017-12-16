#!/usr/bin/python

import sys
import time
from threading import Thread

from Senses import *
from JointController import *

jointController = JointController()

thread = Thread(target = jointController.controlLoop, args = [])
thread.start()

s = Senses()

target1_1 = 0 
target1_2 = 0

target1 = target1_1

tp = time.time()
t0 = tp
e1p = None
hasPlot = False
try:
    while True:
        (f, t) = Senses.getFrame()
        arm = s.findArm(f, 1)
        Senses.showFrame(f)

        if len(arm.segments) == 0 or arm.segments[0].p == None:
            continue

        jointController.setAngle(arm.segments[0].angle, t)

        if t-t0 > 5:
            target1 = target1_2
        if t-t0 > 10:
            target1 = target1_1
            t0 = t
        tp = t

except (SystemExit, KeyboardInterrupt) as e:
    # quit
    print "quit"
    jointController.runControlLoop = False
    Senses.close()
    sys.exit()
except:
    jointController.runControlLoop = False
    Senses.close()
    print "Unexpected error:", sys.exc_info()[0]
    print sys.exc_info()[1]
    print sys.exc_info()[2]
    sys.exit()
