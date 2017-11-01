import cv2
import numpy as np

class Segment:
    def __init__(self, bBox, p):
        self.p = p
        self.bBox = bBox
        self.angle = 0

class Arm:
    def __init__(self):
        self.segments = []
        self.origin = (10,250)

    def writeSegmentNumbers(self, frame):
        n = 1
        for segment in self.segments:
            if segment.bBox == None:
                n = n + 1
                continue
            # Write segment number on center of bounding box
            M = cv2.moments(segment.bBox)
            segmentCenter = (int(M["m10"] / M["m00"])-10, int(M["m01"] / M["m00"])+5)
            cv2.putText(frame, "%2i" % (n), segmentCenter, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
            n = n + 1

    def sortSegments(self):
        newSegments =  []
        previousPoint = self.origin
        while len(self.segments) > 0:
            # Calculate distance from bounding box to previousPoint
            n = 0
            dMin = 100000
            for segment in self.segments:
                d = cv2.pointPolygonTest(segment.bBox, previousPoint, True)
                if abs(d) < dMin:
                    minN = n
                    dMin = abs(d)
                n = n + 1
            if dMin > 200:
                # Did not find segment minN - assume one segment is missing and replace with undefined
                newSegments.append(Segment(None, None))
            nextSegment = self.segments[minN]
            newSegments.append(nextSegment)
            previousPoint = nextSegment.p
            del self.segments[minN]
        self.segments = newSegments

    def drawSegments(self, frame):
        # Draw origin
        cv2.circle(frame, self.origin, 10, (0, 0, 255), -1)
        cv2.drawContours(frame, [segment.bBox for segment in self.segments if segment.bBox != None], -1, (0,0,255), 2)
        for segment in self.segments:
            if segment.p:
                cv2.circle(frame, segment.p, 5, (0, 0, 255), -1)
                cv2.putText(frame, "%6.3f" % (segment.angle), segment.p, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,255,50), 2, cv2.LINE_AA)

    # Segments must be sorted before calling this
    def findAngles(self):
        previousPoint = self.origin
        n = 0
        for segment in self.segments:
            if not segment.p:
                # If a segment is missing then the chain breaks
                break
            d = self.distance(previousPoint, segment.p)
            a = self.angleOfLine(previousPoint, segment.p)
            if n == 0:
                segment.angle = a
            elif n == 1:
                segment.angle = convertDistanceToAngleSegment2(a,d)
                #print "Angle is ", segment.angle
            elif n == 2:
                segment.angle = a
            previousPoint = segment.p
            n = n + 1

    def distance(self, p1, p2):
        return np.linalg.norm((p1[0]-p2[0], p1[1]-p2[1]))

    def angleOfLine(self, p1, p2):
        d = (p2[0]-p1[0], p2[1]-p1[1])
        return np.rad2deg(np.arctan2(d[1], d[0]))

def convertDistanceToAngleSegment2(a, d):
    v = [
        [140, -30],
        [160, -20],
        [184, 0],
        [213, 45],
        [150, 90]
        ]
    #print "In0: ", a, d
    if a < 0:
        if d < v[0][0] or d > 213:
            return -30
        p1 = v[0]
        p2 = v[1]
        n = 1
        while d > p2[0] and n+1 < len(v):
            p1 = v[n]
            p2 = v[n+1]
            n = n+1
        angle = (d-p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0]) + p1[1]
        #print "In1: ", a, d, "out: ", angle, n
        return angle
    if d > 213 or d < v[len(v)-1][0]:
        return 100
    p1 = v[len(v)-2]
    p2 = v[len(v)-1]
    n = len(v)-2
    while d > p1[0] and n > 0:
        p1 = v[n-1]
        p2 = v[n]
        n = n-1
    angle = (d-p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0]) + p1[1]
    #print "In2: ", a, d, "out: ", angle, n
    
    return angle
