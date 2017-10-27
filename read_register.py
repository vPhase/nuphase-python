import nuphase
import sys

reg_adr = int(sys.argv[1])
d=nuphase.Nuphase()
print d.readRegister(0, reg_adr)
print d.readRegister(1, reg_adr)
