import time
import traceback

from Motor import *
from Log import *
from Pid import *

class JointController:
    def __init__(self):
        self.m1 = Motor("m1", 8, 1, 365)
        self.m1.setTarget(150)

        self.m2 = Motor("m2", 9, 0, 365)
        self.m2.setTarget(150)

        self.angleInterval = 2

        self.runControlLoop = True
        
        self.angles =[]
        
        self.targetAngle = 0
        
        self.log = Log(time.time(), "j")
        
        self.pid = Pid(0.3, 0.0, 0.0)

    def setAngle(self, angle, t):
        self.angles.append((t, angle))
    
    def calcAngle(self, t):
        n = len(self.angles)
        if n == 0:
            return 0
        if n >= 1:
            return self.angles[n-1][1]
        if n >= 2:
            dt = self.angles[n-1][0] - self.angles[n-2][0]
            da = self.angles[n-1][1] - self.angles[n-2][1]
            return self.angles[n-1][1] + (t-self.angles[n-1][0]) * da / dt

    def controlLoop(self):
        tp = time.time()
        time.sleep(0.01)
        try:
            while self.runControlLoop:
                t = time.time()
                dt = t - tp
                angle = self.calcAngle(t)

                e = self.targetAngle - angle
                speed = abs(self.pid.f(e, dt))
                if angle > self.targetAngle + self.angleInterval:
                    self.m2.update(dt)
                    self.m1.move(speed)
                elif angle < self.targetAngle - self.angleInterval:
                    self.m1.update(dt)
                    self.m2.move(speed)
                else:
                    self.m1.update(dt)
                    self.m2.update(dt)
    
                self.log.logt(t, "%f %f %f" % (angle, self.targetAngle, speed))
    
                time.sleep(0.03)
                tp = t
            self.m1.setNeutral()
            self.m2.setNeutral()
        except:
            traceback.print_exc()
            print "Unexpected error:", sys.exc_info()[0]
            print sys.exc_info()[1]
            print sys.exc_info()[2]
            self.m1.setNeutral()
            self.m2.setNeutral()
