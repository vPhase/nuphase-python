
import nuphase
import time
import numpy

NUM_TRIES = 100
sys = nuphase.Nuphase()
sys.boardInit(verbose=False)
sys.calPulser(True, readback=True) #turn on cal pulse feature
num_tests=0
num_success=0
num_almost_success=0

for i in range(NUM_TRIES):
    sys.boardInit()  #only deal with buffer 0
    sys.calPulser(True)
    time.sleep(0.2)
    sys.softwareTrigger()
    time.sleep(0.001)
    data = sys.readSysEvent(save=False)
    print sys.getMetaData()
    
    location_of_peaks=[]

    for chan in range(len(data)):
        location_of_peaks.append(numpy.argmax(data[chan]))

    earliest_peak = min(location_of_peaks)
    latest_peak = max(location_of_peaks)

    #condition if peaks caught from multiple pulses
    if (latest_peak - earliest_peak) > 300:
        print i, location_of_peaks, "skipping, trying again..."
        continue

    num_tests=num_tests+1
    #otherwise, try to align
    if location_of_peaks[0] == location_of_peaks[2] == location_of_peaks[4] ==\
       location_of_peaks[6] == location_of_peaks[8] == location_of_peaks[10]:
        print 'alignment successful: ', location_of_peaks
        sys.readSysEvent(save=True, filename='test_alignment.dat') #save pulse event for verification
        num_success=num_success+1
    else:
        print i, 'DATA ARE NOT ALIGNED..', location_of_peaks, earliest_peak, latest_peak
        if abs(latest_peak - earliest_peak) == 1:
            num_almost_success = num_almost_success + 1
            
sys.boardInit()
sys.calPulser(False, readback=True)
print '-------------------------'
print 'RESULTS:', num_success, 'pure successes out of', num_tests, 'tries'
print 'RESULTS:', num_success+num_almost_success, 'almost successes (+/-1) out of', num_tests, 'tries'
