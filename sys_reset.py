import nuphase
import time

sys=nuphase.Nuphase()
sys.reset()
print 'sending reset...'
time.sleep(8)
print sys.readRegister(1,8)
print sys.readRegister(0,8)
