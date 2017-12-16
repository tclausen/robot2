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
    
    def hasAngle(self):
        return len(self.angles) > 0
    
    def calcAngle(self, t):
        n = len(self.angles)
        if n == 0:
            return 0
        return self.angles[n-1][1]

    def calcAngle2(self, t):
        n = len(self.angles)
        if n == 0:
            return 0
        if n >= 1:
            return self.angles[n-1][1]
        if n >= 2:
            dt = self.angles[n-1][0] - self.angles[n-2][0]
            da = self.angles[n-1][1] - self.angles[n-2][1]
            return self.angles[n-1][1] + (t-self.angles[n-1][0]) * da / dt

    def calcForce(self, angle):
        fMax = 750
        fMin = 150
        # Return large force for postive angles
        if angle > 0:
            return min(fMax, 30.0 * angle) + fMin
        else:
            return fMin


    def setMinimumForce(self):
        print "Forces: ", self.m1.force(), self.m2.force()
        if self.m1.force() > 100 and self.m2.force() > 100:
            return
            

    def controlLoop(self):
        t0 = time.time()
        tp = time.time()
        time.sleep(0.01)
        moving = False
        tMoveStart = 0
        self.m1.setTarget(300)
        self.m2.setTarget(300)
        try:
            while self.runControlLoop:
                t = time.time()
                dt = t - tp
                    
                self.setMinimumForce()
                
                if not self.hasAngle():
                    print "Waiting for angle measurement"
                    time.sleep(0.1)
                    continue

                angle = self.calcAngle(t)

                e = self.targetAngle - angle
                #print "a error:", e, self.targetAngle, angle
                if abs(e) < 2:
                    time.sleep(0.02)
                    continue

                #speed = abs(self.pid.f(e, dt))
                speed = 3
                if moving:
                    if t - tMoveStart > 0.2:
                        print "Move stop"
                        self.m1.move(0)
                        self.m2.move(0)
                        moving = False
                        time.sleep(0.02)
                        continue
                    if e > 0:
                        print "Moving down"
                        self.m1.move(-speed)
                        self.m2.move(speed)
                    else:
                        print "Moving up"
                        self.m1.move(speed)
                        self.m2.move(-speed)
                
                if t - t0 > 1:
                    print "---- Reset"
                    moving = True
                    tMoveStart = t
                    t0 = t
    
                self.log.logt(t, "%f %f %f" % (angle, self.targetAngle, speed))
    
                time.sleep(0.02)
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
