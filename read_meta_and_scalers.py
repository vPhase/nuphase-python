import numpy
import nuphase
import time
from bf import *
import json

file_suffix = "16"

d=nuphase.Nuphase()
d.boardInit(True)

d.enablePhasedTrigger(True)
for i in range(15):
    d.setBeamThresholds(19000, i)

time.sleep(5)
print d.readScalers()

print d.getDataManagerStatus()
d.enablePhasedTriggerToDataManager(True)
time.sleep(1)
print d.getDataManagerStatus()

for i in range(4):
    d.setReadoutBuffer(i)
    print i, d.getMetaData()

d.bufferClear(15)


now = time.time()
stop = now + 120
cur_event = 0
NEVENTS=1000
all_metadata=[]
all_scalers=[]
while(now < stop):
    time.sleep(1)
    now = time.time()

    current_scalers = d.readScalers()
    print now, current_scalers
    all_scalers.append(current_scalers)
    
    d.getDataManagerStatus(verbose=False)
    if d.buffer_flags[0] == 0:
        continue

    flags = bf(d.buffer_flags[0])
    for i in range(4):
        if flags[i] == True:
            d.setReadoutBuffer(i)
            metadata = d.getMetaData()
            all_metadata.append(metadata)
            #print cur_event,i,metadata
            cur_event = cur_event + 1

            d.bufferClear(1 << i)
            if metadata['slave']['evt_count'] != metadata['master']['evt_count']:
                print 'EVENT COUNT MISMATCH!!!!!'
                print '....'

d.enablePhasedTriggerToDataManager(False)
with open('test_oct2/metadata_'+file_suffix+'.json', 'w') as f:
    json.dump(all_metadata,f)
with open('test_oct2/scalers_'+file_suffix+'.json','w') as f:
    json.dump(all_scalers,f)
