#!/usr/bin/python
from __future__ import division
import time
import sys
#import spidev
import Adafruit_PCA9685
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

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
    
    def __init__(self, channel, adc, neutral):
        self.channel = channel
        self.adc = adc
        self.neutral = neutral
        self._targetForce = 0
        self.name = "Unset"

        self.ep = 0
        self.totalError = 0

    def setNeutral(self):
        self.move(0)

    def force(self):
        value = Motor.mcp.read_adc(self.adc)
        return value

    def setTarget(self, targetForce):
        self._targetForce = targetForce

    def move(self, v):
        #print "Correction: ", self.name, v
        pwm.set_pwm(self.channel, 0, self.neutral + v)
        pass

    def update(self, dt):
        f = self.force()
        e = self._targetForce - f
        # P term
        p = -0.05 * e
        # D term
        d = 0.009 * (self.ep-e)/dt
        # I term
        self.totalError = self.totalError + e*dt
        i = 0.0 * self.totalError
        i = 0
        
        #print "%s, f: %6.2f, p: %6.2f, d: %6.2f, i: %6.2f, total: %3i" % (self.name, f, p, d, i, int(p + d + i))
        correction = int(p + d + i)
        self.move(correction)
        self.ep = e
