import nuphase
import time
import json
import sys

THRESH_START = 16400
THRESH_END   = 25401
THRESH_INC   = 200

d=nuphase.Nuphase()
d.boardInit()
d.enablePhasedTrigger(enable=True, verification_mode=False)
d.readRegister(1,82)

info={}
current_iter = 0

for i in range(THRESH_START, THRESH_END, THRESH_INC):
    for beam in range(15):
        d.setBeamThresholds(i,beam)
    print 'setting threshold to', i
    print 'wait for scaler to update...'
    time.sleep(20)

    current_scalers = d.readScalers()
    print 'current scaler values:', current_scalers
    info[current_iter] = {}
    info[current_iter]['thresh']  = i
    info[current_iter]['scalers'] = current_scalers
    current_iter = current_iter + 1
    
with open('thresh_scan_all.json', 'w') as f:
    json.dump(info,f)

d.enablePhasedTrigger(enable=False)
    


