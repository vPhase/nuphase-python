#
#   EJO     10/2017
#   write new firmware image to NuPhase board EEPROM
#----------------------------------------
import nuphase
import sys
import time
import reconfigureFPGA as reconfig
import tools.bf as bf

directory = '/home/nuphase/firmware/'
filename = directory+'newfirmware.rpd'

FILEMAP_START_ADDR = 0x00000000
FILEMAP_END_ADDR   = 0x00A3E9B8 
TARGET_START_ADDR  = 0x01000000 #address where application firmware image is stored


def setMode(dev, bus, mode):
    #mode = 1 to write to 256 byte firmware block FIFO
    #mode = 0 to read from block FIFO and cmd the ASMI_PARALLEL block
    dev.write(bus, [0x72, 0x00, 0x00 | mode, 0x00]) 
    updated_mode = dev.readRegister(bus, 0x72)[2]
    return updated_mode

def initWrite(dev, bus):
    current_mode = setMode(dev, bus, 0)
    dev.write(bus, [0x72, 0x01, 0x00 | current_mode, 0x00]) #clear FIFO
    dev.write(bus, [0x72, 0x00, 0x00 | current_mode, 0x00]) #make sure cmd fsm in 'idle' state
    current_mode = setMode(dev, bus, 1) #put block into write mode
    return current_mode

def readStatusReg(dev, bus, verbose=False):
    status = bf.bf(dev.readRegister(bus, 0x67)[3])
    if status[1] == True:
        if verbose:
            print 'EPCQ busy'
        return 'busy'
    elif status[2] == True:
        if verbose:
            print 'DONE'
        return 'done'
    else:
        if verbose:
            print 'uh oh'
        return None

def sectorClear(dev, bus, sector_addr):
    current_mode = setMode(dev, bus, 0)
    sector_addr_list = []
    sector_addr_list.append(int((0x000000FF & sector_addr)))
    sector_addr_list.append(int((0x0000FF00 & sector_addr) >> 8))
    sector_addr_list.append(int((0x00FF0000 & sector_addr) >> 16))
    sector_addr_list.append(int((0xFF000000 & sector_addr) >> 24))
    #write EPCQ address
    dev.write(bus, [0x73, 0x00, sector_addr_list[1], sector_addr_list[0]])
    dev.write(bus, [0x74, 0x00, sector_addr_list[3], sector_addr_list[2]])
    dev.write(bus, [0x72, 0x00, 0x00 | current_mode, 0x04]) #send sector-clear cmd
    while(readStatusReg(dev, bus) != 'done'):
        time.sleep(0.2)
    current_mode = setMode(dev, bus, 1)
    return current_mode

def clearApplicationImage(dev, bus, hw_start_addr, image_end_addr):
    current_address = hw_start_addr + 1
    print 'clearing EEPROM:'
    while(current_address < (image_end_addr + hw_start_addr + 0x1000)):
        sys.stdout.write('   clearing sector address...0x{:x}  \r'.format(current_address-1))
        sys.stdout.flush()
                   
        sectorClear(dev, bus, current_address)
        current_address = current_address + 0x10000
    sys.stdout.write('   clearing sector address...0x{:x}  \n\n'.format(current_address-1))
    print 'DONE WITH EEPROM CLEAR'
    
def writeChunk(dev, bus, byte_list, sector_addr):
    current_mode = (dev, bus, 1)
    dev.write(bus, [0x6F, 0x00, 0x00, 0x01]) #activate write enable to FIFO
    for i in range(0, len(byte_list), 4):
        #--------------------------
        ## Write to FIFO
        ## MSB --> first byte written
        dev.write(bus, [0x71, 0x00, (0xFF & byte_list[i]), (0xFF & byte_list[i+1])])
        dev.write(bus, [0x70, 0x00, (0xFF & byte_list[i+2]), (0xFF & byte_list[i+3])])
        dev.write(bus, [0x6F, 0x00, 0x00, 0x03]) # toggle write clock
        dev.write(bus, [0x6F, 0x00, 0x00, 0x01]) # de-toggle write clock
    #-----------------------
    ## Read bytes from FIFO, toggle write to EEPROM via ASMI_PARALLEL IP core
    current_mode = setMode(dev, bus, 0)
    sector_addr_list = []
    sector_addr_list.append(int((0x000000FF & sector_addr)))
    sector_addr_list.append(int((0x0000FF00 & sector_addr) >> 8))
    sector_addr_list.append(int((0x00FF0000 & sector_addr) >> 16))
    sector_addr_list.append(int((0xFF000000 & sector_addr) >> 24))
    #write EPCQ address
    dev.write(bus, [0x73, 0x00, sector_addr_list[1], sector_addr_list[0]])
    dev.write(bus, [0x74, 0x00, sector_addr_list[3], sector_addr_list[2]])
    #toggle bulk write to EPCQ
    dev.write(bus, [0x72, 0x00, 0x00 | current_mode, 0x02])
    while(readStatusReg(dev, bus) != 'done'):
        time.sleep(0.001)
    current_mode = setMode(dev, bus, 1) #exit test mode
    
def writeFirmwareToEPCQ(dev, bus, filename, FILEMAP_START_ADDR, FILEMAP_END_ADDR):
    # write the firmware image
    #
    start_time = time.time()
    with open(filename, 'rb') as binary_rpd_file:
        binary_rpd_file.seek(0,2)  # Seek the end
        num_bytes = binary_rpd_file.tell()
        print '------------------------'
        print 'Reading raw programming file:', filename
        print 'Filesize:', num_bytes, 'bytes'
        print '------------------------\n'
        
        binary_rpd_file.seek(0,0) # go back to beginning of file
        
        current_address = FILEMAP_START_ADDR
        binary_rpd_file.seek(current_address) # go to start of firmware image in file
        current_byte_in_cycle = 0
        while (current_address < (FILEMAP_END_ADDR+256+1)):
            #--------------
            initWrite(dev, bus)
            #--------------
            epcq_address = current_address + TARGET_START_ADDR
            read_256bytes = binary_rpd_file.read(256)
            write_256bytes = []
            for i in range(256):
                write_256bytes.append(ord(read_256bytes[i]))
            #--------------
            writeChunk(dev, bus, write_256bytes, epcq_address)
            #--------------
            now=time.time()
            _min, _sec = divmod((now-start_time), 60)
            #--------------
            ## print to terminal
            if current_address % pow(2,14) == 0:
                sys.stdout.write('{:.2f} MB written to device; now at EEPROM address 0x{:x}. Time elapsed (min:sec) {:}:{:.1f}         \r'.format((current_address-FILEMAP_START_ADDR)*1e-6, epcq_address, int(_min), _sec))
                sys.stdout.flush()
            #--------------
            current_address = current_address + 256
            
    sys.stdout.write('{:.2f} MB written to device; now at EEPROM address 0x{:x}. Time elapsed (min:sec) {:d}:{:.1f}         \n\n'.format((current_address-FILEMAP_START_ADDR-256)*1e-6, epcq_address, int(_min), _sec))               
    

if __name__=='__main__':

    dev=nuphase.Nuphase()
    bus = dev.BUS_MASTER
    print '\n RUNNING REMOTE FIRMWARE IMAGE UPDATE '
    reconfig.enableRemoteFirmwareBlock(dev, bus, True)
    print '\n***************************\n'
    clearApplicationImage(dev, bus, TARGET_START_ADDR, FILEMAP_END_ADDR)
    print '\n***************************\n'
    time.sleep(1)
    writeFirmwareToEPCQ(dev,bus,filename,FILEMAP_START_ADDR, FILEMAP_END_ADDR)
    reconfig.enableRemoteFirmwareBlock(dev,bus,False)
    print '***************************\n'
    print 'seemed to process successfully'
    
