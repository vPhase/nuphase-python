import nuphase
import time
import json



d=nuphase.Nuphase()
d.enablePhasedTrigger(verification_mode=True)
d.externalTriggerInputConfig(enable=False)
print d.readRegister(1, 75)
for beam in range(15):
    d.setBeamThresholds(22000, beam)


time.sleep(20)

current_scalers = d.readScalers()
print 'current scaler values:', current_scalers



    


