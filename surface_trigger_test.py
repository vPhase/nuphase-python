import nuphase
import time
import json
import sys

THRESH_START = 16400
THRESH_END   = 25401
THRESH_INC   = 200

d=nuphase.Nuphase()
d.boardInit()
bus=1 #plugged in test board into spi bus 1, SP system has slave board in bus=0

d.setSurfaceTriggerConfig(threshold=10, mask=63, min_coinc=3, window=3, hpol=False, fir=True, bus=bus)
d.setSurfaceHpolThreshold(10000, bus=bus)

print d.readRegister(bus,46)
print d.readRegister(bus,47)
print d.readRegister(bus, 102)

print d.readScalers(bus)

while(1):

    time.sleep(1)
    print d.getSurfaceEventFlag(bus=bus)
    d.clearSurfaceEventBuffer(bus=bus)
    d.updateScalerValues(bus=bus)
    
    d.setScalerOut(24, bus=bus)
    print '24: (---, 10second)     :', d.readSingleScaler(bus=bus)
    d.setScalerOut(25, bus=bus)
    print '25: (10sec_gated, 1sec) :', d.readSingleScaler(bus=bus)
    d.setScalerOut(26, bus=bus)
    print '26: (.01second, ---)    :', d.readSingleScaler(bus=bus)
    
