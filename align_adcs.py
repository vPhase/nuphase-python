import nuphase
import time
import numpy

NUM_TRIES = 10
verbose=True

def init(verbose=verbose):
    sys = nuphase.Nuphase()
    sys.boardInit(verbose=verbose)
    current_atten_values = sys.getCurrentAttenValues()
    sys.setAttenValues(numpy.zeros(12, dtype=int), readback=verbose)
    sys.calPulser(True, readback=verbose) #turn on cal pulse feature

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
    
    return sys, SHIFT_BYTES, current_atten_values

def getPeaks(data, mode=1):
    location_of_peaks=[]

    pulse_threshold_master = 84
    pulse_threshold_slave  = 95
    pulse_thresholds = [pulse_threshold_master] * 8
    pulse_thresholds.extend([pulse_threshold_slave]*4)
    
    for chan in range(len(data)):
        ##mode = 0, simply use numpy.argmax
        if mode == 0:
            location_of_peaks.append(numpy.argmax(data[chan]))
            
        ##mode = 1, a bit more complicated and board-specific
        elif mode == 1:
            location_of_peaks.append(numpy.where(numpy.transpose(data[chan]) > pulse_thresholds[chan])[0][0])
            
    return location_of_peaks

            
def align(NUM_TRIES=10):
    sys, SHIFT_BYTES, current_atten_values = init()
    
    DELAY_SLAVE_BY_CLKCYCLE = False
    DELAY_MASTER_BY_CLKCYCLE = False

    for i in range(NUM_TRIES):
        sys.boardInit()  #only deal with buffer 0
        sys.calPulser(True)
        sys.softwareTrigger()
        time.sleep(0.001)
        data = sys.readSysEvent(save=False)
    
        location_of_peaks = getPeaks(data)

        earliest_peak = min(location_of_peaks)
        earliest_peak_ch = numpy.argmin(location_of_peaks)
        latest_peak = max(location_of_peaks)
        latest_peak_ch = numpy.argmax(location_of_peaks)

        #condition if peaks caught from multiple pulses
        if (latest_peak - earliest_peak) > 300:
            if verbose:
                print i, location_of_peaks, "skipping, trying again..."
            continue

        #condition if not within 16 samples, try a dclk reset
        elif (latest_peak - earliest_peak) > 32:
            sys.dclkReset()
            if verbose:
                print 'sending dclk reset to boards..'
            time.sleep(2)
            if verbose:
                print sys.readRegister(1,8), sys.readRegister(0,8)
                print i, location_of_peaks, 'sample diff', latest_peak-earliest_peak
            time.sleep(1)
            sys.boardInit()
            sys.softwareTrigger()
            #dump event
            dat=sys.readSysEvent(save=False)
            continue

        elif (latest_peak - earliest_peak) > 16:
            print 'applying clkcycle delay'
            if earliest_peak_ch > 7:
                DELAY_SLAVE_BY_CLKCYCLE = True
                DELAY_MASTER_BY_CLKCYCLE = False
            else:
                DELAY_MASTER_BY_CLKCYCLE = True
                DELAY_SLAVE_BY_CLKCYCLE = False
            
        #otherwise, try to align
        if location_of_peaks[0] == location_of_peaks[2] == location_of_peaks[4] ==\
           location_of_peaks[6] == location_of_peaks[8] == location_of_peaks[10]:
            if verbose:
                print 'alignment successful: ', location_of_peaks
                print 'SHIFT BYTES:', SHIFT_BYTES
            sys.readSysEvent(save=True, filename='test_alignment.dat') #save pulse event for verification
            close(sys, current_atten_values, verbose=verbose)
            return 1

        if verbose:
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

    close(sys, current_atten_values, verbose=verbose)
    return 0

def close(sys, atten_values, verbose):
    sys.boardInit(verbose=verbose)
    sys.calPulser(False, readback=verbose)
    sys.setAttenValues(atten_values, readback=verbose)

if __name__=="__main__":
    retval=align()
    if retval==0:
        print 'problem here'
