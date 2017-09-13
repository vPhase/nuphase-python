import Adafruit_BBIO.ADC as ADC 
import math

ADC_PIN_MASTER = "P9_39"
ADC_PIN_SLAVE = "P9_37"

def boardTemp():
        volts_master_board = 2.0  * 1.8 * ADC.read(ADC_PIN_MASTER)
        volts_slave_board = 2.0 * 1.8 * ADC.read(ADC_PIN_SLAVE)  #factor of 2 from voltage divider

	## here is the linear-approximate response
	temp_master = (volts_master_board-1.8583)/(-0.01167)
        temp_slave  = (volts_slave_board-1.8583)/(-0.01167)
	return int(temp_master), int(temp_slave)

if __name__=="__main__":
        ADC.setup()
        print boardTemp()
