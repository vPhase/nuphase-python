
import nuphase
import time

sys=nuphase.Nuphase()
sys.calPulser(True, readback=True)
#sys.dclkReset()
#time.sleep(3)

sys.boardInit()
sys.softwareTrigger()
d=sys.readSysEvent(save=True)

sys.calPulser(False, readback=True)
for i in range(len(d)):
    print i, max(d[i])
