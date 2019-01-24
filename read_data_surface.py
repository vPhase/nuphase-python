import numpy
import nuphase
import time
import json
import sys

d=nuphase.Nuphase()
d.boardInit(True)
#d.calPulser(True)
#d.externalTriggerInputConfig(enable=True)

bus=1


for i in range(4):
    d.clearSurfaceEventBuffer(bus=bus)
    time.sleep(1)

    if d.getSurfaceEventFlag(bus):
        d.setSurfaceReadout(True, bus=bus)
        data = d.readBoardEvent(bus, address_stop=128)
        numpy.savetxt('test_surface_'+str(i)+'.dat', numpy.array(data, dtype=numpy.int8))
        print 'saving event', i

    d.setSurfaceReadout(False, bus=bus)
    
        
        

    


