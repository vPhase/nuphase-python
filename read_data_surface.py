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

i=0
while(i <4):
    ##software triggers:
    #d.softwareTrigger()
    #d.setReadoutBuffer(i)
    #d.getMetaData(True)

    
    d.clearSurfaceEventBuffer(bus=bus)
    time.sleep(1)

    if d.getSurfaceEventFlag(bus):
        d.setSurfaceReadout(True, bus=bus)
        
        d.getMetaData(True)
        data = d.readBoardEvent(bus, address_stop=128)
        numpy.savetxt('test_surface_'+str(i)+'.dat', numpy.array(data, dtype=numpy.int8))
        print 'saving event', i
        i=i+1
        
    d.setSurfaceReadout(False, bus=bus)
    
        
        

    


