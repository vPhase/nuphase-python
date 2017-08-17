# ADC board Interface to BeagleBone Black (industrial version)
# using SPI0 interface:
# ---> CS   = P9_17
# ---> CLK  = P9_22
# ---> MOSI = P9_18
# ---> MISO = P9_21
#

from Adafruit_BBIO import SPI
import Adafruit_BBIO.GPIO as GPIO
import math
import time

class Nuphase():
    spi_bytes = 4  #transaction must include 4 bytes
    firmware_registers_adr_max=128
    firmware_ram_adr_max=128

    map = {
        'FIRMWARE_VER'  : 0x01,
        'FIRMWARE_DATE' : 0x02,
        'SET_READ_REG'  : 0x6D, #pick readout register
        'READ'          : 0x47, #send data to spi miso
        'FORCE_TRIG'    : 0x40, #software trigger
        'CHANNEL'       : 0x41, #select channel to read
        'CHUNK'         : 0x49, #select 32-bit chunk of data in 128-wide bus
        'RAM_ADR'       : 0x45, #ram address
        'MODE'          : 0x42, #select readout mode
        'CALPULSE'      : 0x2A, #toggle RF switch/pulser board
        }
        
    readout_mode = {
        'REGISTER'      : 0,
        'WAVEFORMS'     : 1,
        'BEAMS'         : 2,
        'POWERSUM'      : 3,
        }

    def __init__(self, dev=0,spi_clk_freq=10000000):
        GPIO.setup("P9_12", GPIO.OUT) #enable pin for 2.5V bus drivers
        GPIO.output("P9_12", GPIO.LOW)  #enable for 2.5V bus drivers
        self.spi0=SPI.SPI(dev,0) #setup SPI0
        self.spi0.mode = 0
        try:
            self.spi0.msh = spi_clk_freq
        except IOError:
            pass #hardware does not support this speed..
    
    def write(self, data):
        if len(data) != 4:
            return None
        
        self.spi0.writebytes(data)        

    def read(self):
        return self.spi0.readbytes(self.spi_bytes)

    def readRegister(self, address=1):
        if address > self.firmware_registers_adr_max-1 or address < 0:
            return None

        ## set readout register
        send_word=[self.map['SET_READ_REG'], 0x00, 0x00, address & 0xFF]
        self.write(send_word) #set read register of interest
        readback = self.read()
        
        return readback

    def dna(self):
        dna_bytes = 8
        
        dna_low = self.readRegister(4) #lower 3 bytes 
        dna_mid = self.readRegister(5) #middle 3 bytes
        dna_hi  = self.readRegister(6) #upper 2 bytes
        
        print dna_hi, dna_mid, dna_low
        board_dna = 0
        for i in range(dna_bytes):
            if i < 3:
                board_dna = board_dna | dna_low[i] << i*8
            elif i < 6:
                board_dna = board_dna | dna_mid[i-3] << i*8
            else:
                board_dna = board_dna | dna_hi[i-6] << i*8
            
        return board_dna

    def identify(self):
        firmware_version = self.readRegister(self.map['FIRMWARE_VER'])
        print 'firmware version:', firmware_version
        firmware_date = self.readRegister(self.map['FIRMWARE_DATE'])
        print 'firmware date:', firmware_date
        dna = self.dna()
        print 'board DNA:', dna

    def reset(self):
        self.write([127,0,0,1])

    def readRamAddress(self, address):
        data=[]
        self.write([69,0,0, 0x7F & address])
        time.sleep(0.001)
        self.write([35,0,0,0])
        data.extend(self.read())
        self.write([36,0,0,0])
        data.extend(self.read())
        self.write([37,0,0,0])
        data.extend(self.read())
        self.write([38,0,0,0])
        data.extend(self.read())

        return data
