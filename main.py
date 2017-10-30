#!/usr/bin/python

import sys
import time
from threading import Thread

from Senses import *
from Motor import *

m1 = Motor(8, 1)
m1.name = "m1"
m1.setTarget(100)

m2 = Motor(9, 0)
m2.name = "m2"
m2.setTarget(100)

runControlLoop = True

def controlLoop():
    global runControlLoop
    tp = time.time()
    time.sleep(0.01)
    while runControlLoop:
        t = time.time()
        dt = t - tp 

        #m1.update(dt)
        #m2.update(dt)
    
        time.sleep(0.01)
        tp = t

thread = Thread(target = controlLoop, args = [])
thread.start()

s = Senses()

target1_1 = 10
target1_2 = -10

target1 = target1_1

tp = time.time()
t0 = tp
e1p = None
e2p = None
e2 = 0
errors1 = []
ts = []
hasPlot = False
try:
    while True:
        (f, t) = Senses.getFrame()
        arm = s.findArm(f, 1, 0)
        Senses.showFrame(f)

        if len(arm.segments) == 0 or arm.segments[0].p == None:
            continue
        
        #print "e1 %f" % (e1)
        #j1.move(e1, e1p, t-tp)
        if t-t0 > 5:
            target1 = target1_2
        if t-t0 > 10:
            target1 = target1_1
            t0 = t
        ts.append(t-t0)
        #print target1, t, t0

        #errors1.append(e1)
        #e1p = e1
        tp = t
                
except KeyboardInterrupt:
    # quit
    print "quit"
    runControlLoop = False
    Senses.close()
    sys.exit()
