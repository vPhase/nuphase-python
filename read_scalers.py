import nuphase
import time
import json



d=nuphase.Nuphase()
d.enablePhasedTrigger()

current_scalers = d.readScalers()
print 'current scaler values:', current_scalers



    


