#!/usr/bin/python
from __future__ import division
import time
import sys
#import spidev
import Adafruit_PCA9685
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

from Log import *
from Pid import *

pwm = Adafruit_PCA9685.PCA9685()
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

#spi = spidev.SpiDev()
#spi.open(0, 0)


targetForce = 100
neutral = 366

def readadc(adcnum):
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

class Motor:
    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0
    mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
    
    def __init__(self, name, channel, adc, neutral):
        self.channel = channel
        self.adc = adc
        self.neutral = neutral
        self._targetForce = 0
        self.name = name
        self.targetForceMin = 10
        self.targetForceMax = 800
        
        self.pid = Pid(0.02, 0, 0)
        
        self.log = Log(time.time(), "m_"+self.name)

    def setNeutral(self):
        self.move(0)

    def force(self):
        value = Motor.mcp.read_adc(self.adc)
        return value

    def setTarget(self, targetForce):
        if targetForce > self.targetForceMax:
            targetForce = self.targetForceMax
        elif targetForce < self.targetForceMin:
            targetForce = self.targetForceMin
        self._targetForce = targetForce

    def move(self, v):
        #print "Correction: ", self.name, v
        pwm.set_pwm(self.channel, 0, self.neutral + v)

    def update(self, dt):
        f = self.force()
        e = self._targetForce - f
        
        #~ if f < 2:
            #~ self.move(0)
            #~ return
            
        correction = self.pid.f(e, dt)
        self.log.logt(time.time(), "%f %f %i" % (f, self._targetForce, correction))
        self.move(correction)
        self.ep = e
