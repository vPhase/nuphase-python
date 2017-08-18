
import nuphase
import time
import numpy

NUM_TRIES = 10
sys = nuphase.Nuphase()
sys.boardInit()
sys.calPulser(True) #turn on cal pulse feature

for i in range(NUM_TRIES):
    sys.boardInit()  #only deal with buffer 0
    time.sleep(0.001)
    sys.softwareTrigger()
    time.sleep(0.001)
    data = sys.readSysEvent(save=False)
    
    location_of_peaks=[]

    for chan in range(len(data)):
        location_of_peaks.append(numpy.argmax(data[chan]))

    earliest_peak = min(location_of_peaks)
    latest_peak = max(location_of_peaks)

    #condition if peaks caught from multiple pulses
    if (latest_peak - earliest_peak) > 300:
        continue
    #condition if not within 16 samples, try a dclk reset
    elif (latest_peak - earliest_peak) > 15:
        sys.dclkReset()
        print 'sending dclk reset to boards..'
        time.sleep(0.5)
        continue

    #otherwise, try to align
    if location_of_peaks[0] == location_of_peaks[2] == location_of_peaks[4] ==\
       location_of_peaks[6] == location_of_peaks[8] == location_of_peaks[10]:
        print 'alignment successful'
        sys.readSysEvent(save=True, filename='test_alignment.dat') #save pulse event for verification
        break

    shift_value=numpy.zeros(6, dtype=int)
    #system has 12 channels = 6 ADC shift values
    for j in range(6):
        shift_value[j] = latest_peak-location_of_peaks[2*j]+1
        #write to master if i =[0,3]
        if shift_value[j] != 0:
            shift_word_low_byte = 0x00 | (shift_value[j] & 0x7) << 5 | True << 4 | (shift_value[j] & 0xF)
            shift_word_hi_byte = 0x00 | True << 1 | (shift_value[j] & 0x8) >> 3
            print shift_word_low_byte, shift_word_hi_byte
            if j < 4:
                sys.write(1, [56+j,0,shift_word_hi_byte, shift_word_low_byte])
            else:
                sys.write(0, [56+j-4,0,shift_word_hi_byte, shift_word_low_byte])
        time.sleep(0.001)
    
sys.boardInit()
sys.calPulser(False, readback=True)
