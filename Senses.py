import sys
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2

from Arm import *
from Log import *

#assign strings for ease of coding
hh='Hue High'
hl='Hue Low'
sh='Saturation High'
sl='Saturation Low'
vh='Value High'
vl='Value Low'
wnd = 'Colorbars'

def nothing(self):
    pass
 
class Senses:
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.rotation = 270
    camera.saturation = 40
    # initialize the camera and grab a reference to the raw camera capture
    camera.framerate = 40
    rawCapture = PiRGBArray(camera, size=(640, 480))
    
    def __init__(self):
        # define the lower and upper boundaries of the "blue"
        # ball in the HSV color space
        self.oLower = (90, 130, 150)
        self.oUpper = (116, 255, 255)
        self.iLower = (120, 0, 0)
        self.iUpper = (255, 255, 255)
        #self.oLower = (90, 0, 0)
        #self.oUpper = (120, 255, 255)
        #self.iLower = (120, 0, 0)
        #self.iUpper = (255, 255, 255)
        self.log = Log(time.time(), "s")
        
    def showTrackbars(self, lower, upper):
        cv2.namedWindow('Colorbars') 
 
        #Begin Creating trackbars for each
        cv2.createTrackbar(hl, wnd,0,179,nothing)
        cv2.setTrackbarPos(hl, wnd, lower[0])
        
        cv2.createTrackbar(hh, wnd,0,179,nothing)
        cv2.setTrackbarPos(hh, wnd, upper[0])
        
        cv2.createTrackbar(sl, wnd,0,255,nothing)
        cv2.setTrackbarPos(sl, wnd, lower[1])
        
        cv2.createTrackbar(sh, wnd,0,255,nothing)
        cv2.setTrackbarPos(sh, wnd, upper[1])
        
        cv2.createTrackbar(vl, wnd,0,255,nothing)
        cv2.setTrackbarPos(vl, wnd, lower[2])
        
        cv2.createTrackbar(vh, wnd,0,255,nothing)
        cv2.setTrackbarPos(vh, wnd, upper[2])
        
    @staticmethod
    def close():
        Senses.camera.close()

    @staticmethod
    def showFrame(frame):
        cv2.imshow("Image", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            sys.exit()
        
    @staticmethod
    def getFrame():
        Senses.rawCapture.truncate(0)
        Senses.camera.capture(Senses.rawCapture, format="bgr", use_video_port=True)
        image = Senses.rawCapture.array
        return (image, time.time())

    @staticmethod
    def saveFrame(i, frame):
        filename = "obj-" + str(i) + ".jpg"
        print ("Writing file %s" % filename)
        cv2.imwrite(filename, frame)

    def getColorsFromTrackbars(self):
        # read trackbar positions for each trackbar
        hul=cv2.getTrackbarPos(hl, wnd)
        huh=cv2.getTrackbarPos(hh, wnd)
        sal=cv2.getTrackbarPos(sl, wnd)
        sah=cv2.getTrackbarPos(sh, wnd)
        val=cv2.getTrackbarPos(vl, wnd)
        vah=cv2.getTrackbarPos(vh, wnd)

        HSVLOW=np.array([hul,sal,val])
        HSVHIGH=np.array([huh,sah,vah])

        return (HSVLOW, HSVHIGH)

    def translate(self, contour, dx, dy):
        c = np.copy(contour)
        for p in c:
            if len(p) < 2:
                p = p[0]
            p[0] = p[0] + dx
            p[1] = p[1] + dy
        return c
            
    def findArm(self, frame, nArms):
        startTime = time.time()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = None
        useSliders = False
        if useSliders:
            (l, h) = self.getColorsFromTrackbars()
            mask = cv2.inRange(hsv, l, h)
        else:
            mask = cv2.inRange(hsv, self.oLower, self.oUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        #cv2.imshow(self.name, mask)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        armContours = []
        if len(cnts) > 0:
            sortedContours = sorted(cnts, key=cv2.contourArea, reverse=True)
            for n in range(min(len(sortedContours), nArms)):
                contour = sortedContours[n]
                rect = cv2.minAreaRect(contour)
                box = np.int0(cv2.boxPoints(rect))
                armContours.append(box)
        else:
            return Arm()
        useSliders = False
        arm = Arm()
        for armContour in armContours:
            x,y,w,h = cv2.boundingRect(armContour)
            #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            # Find point in cropped image
            mask2 = 0
            if useSliders:
                (low, high) = self.getColorsFromTrackbars()
                mask2 = cv2.inRange(hsv[y:y+h, x:x+w], low, high)
            else:
                mask2 = cv2.inRange(hsv[y:y+h, x:x+w], self.iLower, self.iUpper)
            if mask2 is None:
                continue
            # Generate mask of segment in cropped image
            armMask2 = np.zeros(mask2.shape, dtype=np.uint8)
            armContourTranslated = self.translate(armContour, -x, -y)
            cv2.drawContours(armMask2, [armContourTranslated], 0, (255,255,255), cv2.FILLED)
            # Bitwise and mask of segment and mask of point to only get points inside segment (in cropped image)
            mask2 = cv2.bitwise_and(armMask2, mask2)
            # Now find contour of point
            cnts = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(cnts) > 0:
                # Sort on area to find largest contour 
                sortedContours = sorted(cnts, key=cv2.contourArea, reverse=True)
                contour0 = sortedContours[0]
                # Extract center of point
                M0 = cv2.moments(contour0)
                if M0["m00"] > 0:
                    center0 = (int(M0["m10"] / M0["m00"]) + x, int(M0["m01"] / M0["m00"]) + y)
                    arm.segments.append(Segment(armContour, center0))
            #cv2.imshow(self.name+"inner %s" % n, mask1)

        # Sort segments on distance to previous point
        arm.sortSegments()

        # Segments must be sorted before running this
        arm.findAngles()
        arm.writeSegmentNumbers(frame)
        arm.drawSegments(frame)
        
        if len(arm.segments) > 0:
            positionsText = ""
            for s in arm.segments:
                positionsText = positionsText + " %f" % (s.angle)
        
            self.log.log("%f %s" %(startTime, positionsText))
        else:
            self.log.log("")

        endTime = time.time()
        cv2.putText(frame, "Process time: %7.4f s" % (endTime-startTime), (10,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        return arm

    
