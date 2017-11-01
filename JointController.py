from Motor import *

class JointController:
    def __init__(self):
        self.m1 = Motor("m1", 8, 1, 365)
        self.m1.setTarget(150)

        self.m2 = Motor("m2", 9, 0, 365)
        self.m2.setTarget(150)

        self.runControlLoop = True


    def controlLoop(self):
        tp = time.time()
        time.sleep(0.01)
        try:
            while self.runControlLoop:
                t = time.time()
                dt = t - tp 
    
                self.m1.update(dt)
                self.m2.update(dt)
    
                time.sleep(0.01)
                tp = t
            self.m1.setNeutral()
            self.m2.setNeutral()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print sys.exc_info()[1]
            print sys.exc_info()[2]
            self.m1.setNeutral()
            self.m2.setNeutral()
