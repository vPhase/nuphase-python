import numpy
import nuphase

TARGET_NOISE_RMS_COUNTS = 4

def getRMS(data):
    rms = []
    for i in range(len(data)):
        rms.append(round(numpy.std(data[i]),2))

    return rms
    

dev=nuphase.Nuphase()
dev.boardInit()
dev.softwareTrigger()
data = dev.readSysEvent()
rms = getRMS(data)
print dev.getCurrentAttenValues()
print rms

#set_atten_values = numpy.ones(12, dtype=int) * 0
#dev.setAttenValues(set_atten_values)
#dev.boardInit()
#dev.softwareTrigger()
#data=dev.readSysEvent()
#print getRMS(data)

