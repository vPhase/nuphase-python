import numpy
import nuphase
import time
import sys

TARGET_NOISE_RMS_COUNTS = 4

def getRMS(data):
    rms = []
    for i in range(len(data)):
        rms.append(round(numpy.std(data[i]),2))

    return rms

def reverseBitsInByte(data):
    reversed_bytes=[]
    for i in range(len(data)):
        reversed_bytes.append(int('{:08b}'.format(data[i])[::-1],2))

    return reversed_bytes
        
dev=nuphase.Nuphase()
dev.boardInit()
set_atten_values = numpy.ones(12, dtype=int) * 1
set_atten_values = reverseBitsInByte(set_atten_values)
dev.setAttenValues(set_atten_values)

done=False

while(done==False):
    dev.boardInit()
    dev.softwareTrigger()
    data=dev.readSysEvent()
    current_atten_values = dev.getCurrentAttenValues()
    reversed_current_atten_values = reverseBitsInByte(current_atten_values)
    
    rms=getRMS(data)
    print 'rms:', rms
    check_good = 0
    for i in range(len(rms)):
        if rms[i] < TARGET_NOISE_RMS_COUNTS:
            continue
        else:
            check_good = check_good + 1
            reversed_current_atten_values[i] = reversed_current_atten_values[i] + 1
       
    current_atten_values = reverseBitsInByte(reversed_current_atten_values)
    dev.setAttenValues(current_atten_values, readback=False)

    print 'current atten values:', dev.getCurrentAttenValues()
    print 'reversed bits:', reversed_current_atten_values
    print '------'
    if check_good == 0:
        done = True
    time.sleep(0.5)
 
print 'done'
