import writeEPCQ
import sys
import nuphase
import time
import reconfigureFPGA as reconfig

dev=nuphase.Nuphase()
bus = dev.BUS_MASTER

#writeEPCQ.clearApplicationImage(dev, bus, writeEPCQ.TARGET_START_ADDR, writeEPCQ.FILEMAP_END_ADDR)

#writeEPCQ.readEPCQBlock(dev, bus, writeEPCQ.TARGET_START_ADDR)
#byte_list = []
#file_byte_list = []

start_address = writeEPCQ.TARGET_START_ADDR
end_address   = writeEPCQ.FILEMAP_END_ADDR + writeEPCQ.TARGET_START_ADDR 
filename      = writeEPCQ.filename

reconfig.enableRemoteFirmwareBlock(dev, bus, False)
reconfig.enableRemoteFirmwareBlock(dev, bus, True)

with open(filename, 'rb') as binary_rpd_file:

    binary_rpd_file.seek(0)
    for j in range(start_address, end_address, 16384):

        if (j % (pow(2,20))) == 0:
            print 'have read', (j-start_address) * 1.e-6, 'MB of data'
            
        writeEPCQ.readEPCQBlock(dev, bus, j)
        for i in range(4096):
            
            true_byte_list=[]
            for k in range(4):
                true_byte_list.append(ord(binary_rpd_file.read(1)))
            true_byte_list=true_byte_list[::-1]

            byte_list=[]
            dev.write(bus, [0x79, 0x00, 0x00, 0x01])
            addr=[]
            addr.append(int((0x0000FF & i)))
            addr.append(int((0x00FF00 & i) >> 8))
            addr.append(int((0xFF0000 & i) >> 16))
            
            dev.write(bus, [0x78, addr[2], addr[1], addr[0]])
            dev.write(bus, [0x79, 0x00, 0x00, 0x03])
            dat = dev.readRegister(bus, 0x6A)
            #print hex(j), i, dat[3],dat[2],
            byte_list.append(dat[3])
            byte_list.append(dat[2])
            dat = dev.readRegister(bus, 0x6B)
            #print dat[3],dat[2]
            byte_list.append(dat[3])
            byte_list.append(dat[2])

            error = 0
            for k in range(4):
                if true_byte_list[k] != byte_list[k]:
                    print 'BYTE MISMATCH', hex(j), i, k, true_byte_list[k], byte_list[k]
                    error = error+1
            if error > 0:
                print 'uh oh'
                time.sleep(0.5)
            
reconfig.enableRemoteFirmwareBlock(dev, bus, False)    
