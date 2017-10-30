#!/usr/bin/python
from __future__ import division
import time
import sys
import spidev

adc = int(sys.argv[1])

spi = spidev.SpiDev()
spi.open(0, 0)

def readadc(adcnum):
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

while True:
    d = readadc(adc)
    print d
    time.sleep(0.1)
