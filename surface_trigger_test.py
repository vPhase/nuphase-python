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

d.setSurfaceTriggerConfig(threshold=15, mask=63, min_coinc=2, bus=bus)

print d.readRegister(bus,46)
print d.readRegister(bus,47)

print d.readScalers(bus)

while(1):

    print d.getSurfaceEventFlag(bus=bus)
    d.clearSurfaceEventBuffer(bus=bus)
    d.updateScalerValues(bus=bus)
    
    d.setScalerOut(24, bus=bus)
    print '24', d.readSingleScaler(bus=bus)
    d.setScalerOut(25, bus=bus)
    print '25', d.readSingleScaler(bus=bus)
    time.sleep(1)
    
