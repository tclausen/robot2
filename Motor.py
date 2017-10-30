#!/usr/bin/python
from __future__ import division
import time
import sys
import spidev
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

spi = spidev.SpiDev()
spi.open(0, 0)

targetForce = 100
neutral = 366

def readadc(adcnum):
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

class Motor:
    def __init__(self, channel, adc):
        self.channel = channel
        self.adc = adc
        self.neutral = 366
        self._targetForce = 0
        self.name = "Unset"

        self.ep = 0
        self.totalError = 0

    def force(self):
        return readadc(self.adc)

    def setTarget(self, targetForce):
        self._targetForce = targetForce

    def move(self, v):
        #print "Correction: ", self.name, v
        pwm.set_pwm(self.channel, 0, self.neutral + v)

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
        correction = int(p + d + i)
        self.move(correction)
        self.ep = e
