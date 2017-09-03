import numpy
import nuphase
import time
from bf import *
import json
import sys

d=nuphase.Nuphase()
d.boardInit(True)

d.enablePhasedTrigger(True)


if len(sys.argv) == 2:
    thresh = int(sys.argv[1])
    for i in range(15):
        d.setBeamThresholds(thresh, i)

    time.sleep(15)

print d.readAllThresholds()
print d.readScalers()

print d.getDataManagerStatus()
d.enablePhasedTriggerToDataManager(True)
time.sleep(5)
print d.getDataManagerStatus()
d.enablePhasedTriggerToDataManager(False)

for i in range(4):
    d.setReadoutBuffer(i)
    print i, d.getMetaData()
    d.readSysEvent(save=True, filename='test'+str(i)+'.dat')



