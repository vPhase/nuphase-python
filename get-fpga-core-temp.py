import numpy
import nuphase

d=nuphase.Nuphase()
temp_cntl_reg = 108
temp_bits_reg = 6
temps=[]

for dev in range(2):
    
    d.write(dev, [temp_cntl_reg, 0, 0, 1])
    d.write(dev, [temp_cntl_reg, 0, 0, 3])
    temps.append(d.readRegister(dev,temp_bits_reg)[1]-128)
    d.write(dev, [temp_cntl_reg, 0, 0, 0])
    #print d.readRegister(dev, temp_cntl_reg) #should be all zeros, don't want to leave ADC on!
    print 'temp of FPGA at SPI dev', dev, ': ', temps[dev], 'C'
