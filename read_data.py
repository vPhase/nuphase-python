import numpy
import nuphase
import time
from bf import *
import json

d=nuphase.Nuphase()
d.boardInit(True)

d.enablePhasedTrigger(True)
for i in range(15):
    d.setBeamThresholds(38000, i)

time.sleep(15)
print d.readScalers()

print d.getDataManagerStatus()
d.enablePhasedTriggerToDataManager(True)
time.sleep(1)
print d.getDataManagerStatus()

for i in range(4):
    d.setReadoutBuffer(i)
    print i, d.getMetaData()

d.bufferClear(15)

cur_event = 0
NEVENTS=10
all_metadata=[]
while(cur_event < NEVENTS):
    time.sleep(0.0001)
    d.getDataManagerStatus(verbose=False)
    if d.buffer_flags[0] == 0:
        continue

    flags = bf(d.buffer_flags[0])
    for i in range(4):
        if flags[i] == True:
            d.setReadoutBuffer(i)
            metadata = d.getMetaData()
            all_metadata.append(metadata)
            print cur_event,i,metadata
            cur_event = cur_event + 1

            d.bufferClear(1 << i)
            if metadata['slave']['evt_count'] != metadata['master']['evt_count']:
                print 'EVENT COUNT MISMATCH!!!!!'
                print '....'

d.enablePhasedTriggerToDataManager(False)
with open('metadata.json', 'w') as f:
    json.dump(all_metadata,f)
