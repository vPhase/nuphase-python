import nuphase
import time
import json

THRESH_START = 0x000FFF
THRESH_END   = 0x00CFFF
THRESH_INC   = 2048

d=nuphase.Nuphase()
d.enablePhasedTrigger()

info={}

for i in range(THRESH_START, THRESH_END, THRESH_INC):
    d.setBeamThresholds(i)
    print 'setting threshold to', i
    print 'wait for scaler to update...'
    time.sleep(15)

    current_scalers = d.readScalers()
    print 'current scaler values:', current_scalers
    info[i] = current_scalers

with open('thresh_scan.json', 'w') as f:
    json.dump(info,f)

d.enablePhasedTrigger(False)
    


