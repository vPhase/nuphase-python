import numpy
import nuphase
import time
import json
import sys

d=nuphase.Nuphase()
d.boardInit(True)
#d.calPulser(True)
#d.externalTriggerInputConfig(enable=True)
'''
d.enablePhasedTrigger(True, verification_mode=True)

thresh=20000

#if len(sys.argv) == 2:
    #thresh = int(sys.argv[1])

for i in range(15):
    d.setBeamThresholds(thresh, i)
time.sleep(15)

print d.readAllThresholds()
print d.readScalers()

#print d.getDataManagerStatus()
#d.enablePhasedTriggerToDataManager(True)
#time.sleep(5)
#print d.getDataManagerStatus()
#d.enablePhasedTriggerToDataManager(False)


d.enablePhasedTriggerToDataManager(False)
d.eventInit()
time.sleep(2)
d.enablePhasedTriggerToDataManager(True)

time.sleep(10)
'''

time.sleep(1)
for i in range(4):
    d.softwareTrigger() 
    d.setReadoutBuffer(i)
    print i, d.getMetaData()
    data = d.readSysEvent(save=True, address_stop=128, filename='test'+str(i)+'.dat')

    for j in range(len(data)):
        print 'ch', j, 'rms=', numpy.std(data[j])

d.enablePhasedTriggerToDataManager(False)


