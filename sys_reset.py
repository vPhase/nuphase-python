import nuphase
import time

sys=nuphase.Nuphase()
sys.reset()
print 'sending reset...'
time.sleep(20)
print sys.readRegister(1,8)
print sys.readRegister(0,8)

sys.boardInit()
sys.softwareTrigger()
sys.readSysEvent(save=False)
sys.boardInit()
