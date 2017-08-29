
import nuphase
import time
import numpy

NUM_TRIES = 10
sys = nuphase.Nuphase()
sys.boardInit(verbose=True)
sys.calPulser(True, readback=True) #turn on cal pulse feature

DELAY_SLAVE_BY_CLKCYCLE = False
DELAY_MASTER_BY_CLKCYCLE = False
SHIFT_BYTES = numpy.zeros(12, dtype=int)

#set to 0 and read in current values for delay:
for i in range(4):
    sys.write(sys.BUS_MASTER, [56+i,0,0,0])
    readback = sys.readRegister(sys.BUS_MASTER, 56+i) 
    SHIFT_BYTES[2*i] = readback[3]
    SHIFT_BYTES[2*i+1] = readback[2]
for i in range(2):
    sys.write(sys.BUS_SLAVE, [56+i,0,0,0])
    readback = sys.readRegister(sys.BUS_SLAVE, 56+i)
    SHIFT_BYTES[2*i+8] = readback[3]
    SHIFT_BYTES[2*i+1+8] = readback[2]

print 'current shift values', SHIFT_BYTES
    
for i in range(NUM_TRIES):
    sys.boardInit()  #only deal with buffer 0
    sys.softwareTrigger()
    time.sleep(0.001)
    data = sys.readSysEvent(save=False)
    
    location_of_peaks=[]

    for chan in range(len(data)):
        location_of_peaks.append(numpy.argmax(data[chan]))

    earliest_peak = min(location_of_peaks)
    earliest_peak_ch = numpy.argmin(location_of_peaks)
    latest_peak = max(location_of_peaks)
    latest_peak_ch = numpy.argmax(location_of_peaks)

    #condition if peaks caught from multiple pulses
    if (latest_peak - earliest_peak) > 300:
        print i, location_of_peaks, "skipping, trying again..."
        continue

    #condition if not within 16 samples, try a dclk reset
    elif (latest_peak - earliest_peak) > 32:
        sys.dclkReset()
        print 'sending dclk reset to boards..'
        time.sleep(2)
        print sys.readRegister(1,8), sys.readRegister(0,8)
        print i, location_of_peaks, 'sample diff', latest_peak-earliest_peak
        time.sleep(1)
        sys.boardInit()
        sys.softwareTrigger()
        #dump event
        dat=sys.readSysEvent(save=False)
        continue

    elif (latest_peak - earliest_peak) > 16:
        if earliest_peak_ch > 7:
            DELAY_SLAVE_BY_CLKCYCLE = True
            DELAY_MASTER_BY_CLKCYCLE = False
        else:
            DELAY_MASTER_BY_CLKCYCLE = True
            DELAY_SLAVE_BY_CLKCYCLE = False
        
            
    #otherwise, try to align
    if location_of_peaks[0] == location_of_peaks[2] == location_of_peaks[4] ==\
       location_of_peaks[6] == location_of_peaks[8] == location_of_peaks[10]:
        print 'alignment successful: ', location_of_peaks
        print 'SHIFT BYTES:', SHIFT_BYTES
        sys.readSysEvent(save=True, filename='test_alignment.dat') #save pulse event for verification
        break

    print location_of_peaks, 'sample diff', latest_peak-earliest_peak
    #system has 12 channels = 6 ADC shift values
    for j in range(4):
        shift_value = latest_peak+DELAY_MASTER_BY_CLKCYCLE*16-location_of_peaks[2*j]+1
        if shift_value != 0:
            #should be identical for both channels within an ADC
            SHIFT_BYTES[2*j] = 0x00 | DELAY_MASTER_BY_CLKCYCLE << 5 | True << 4 | (shift_value & 0xF)
            SHIFT_BYTES[2*j+1] = 0x00 | DELAY_MASTER_BY_CLKCYCLE << 5 | True << 4 | (shift_value & 0xF)
            sys.write(sys.BUS_MASTER, [56+j,0,SHIFT_BYTES[2*j+1], SHIFT_BYTES[2*j]])

    for j in range(2):
        shift_value = latest_peak+DELAY_SLAVE_BY_CLKCYCLE*16-location_of_peaks[2*j+8]+1
        if shift_value != 0:
            #should be identical for both channels within an ADC
            SHIFT_BYTES[2*j+8] = 0x00 | DELAY_SLAVE_BY_CLKCYCLE << 5 | True << 4 | (shift_value & 0xF)
            SHIFT_BYTES[2*j+1+8] = 0x00 | DELAY_SLAVE_BY_CLKCYCLE << 5 | True << 4 | (shift_value & 0xF)
            sys.write(sys.BUS_SLAVE, [56+j,0,SHIFT_BYTES[2*j+1+8],SHIFT_BYTES[2*j+8]])

            
sys.boardInit()
sys.calPulser(False, readback=True)
