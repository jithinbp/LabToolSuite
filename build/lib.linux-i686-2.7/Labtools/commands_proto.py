import math,sys,time

ACKNOWLEDGE = 254

#/*----flash memory----*/
FLASH =1
READ_FLASH  = 1
WRITE_FLASH = 2
WRITE_BULK_FLASH = 3
READ_BULK_FLASH = 4

#/*-----ADC------*/
ADC =2
CAPTURE_ONE= 1
CAPTURE_TWO= 2
CAPTURE_FOUR =4
CONFIGURE_TRIGGER =5
GET_CAPTURE_STATUS= 6
GET_CAPTURE_CHANNEL= 7
SET_PGA_GAIN= 8
GET_VOLTAGE =9
GET_VOLTAGE_SUMMED= 10
START_ADC_STREAMING =11
SELECT_PGA_CHANNEL=12
CAPTURE_12BIT= 13

#/*-----SPI--------*/
SPI_HEADER =3
START_SPI =1
SEND_SPI8= 2
SEND_SPI16= 3
STOP_SPI =4
SET_SPI_PARAMETERS =5
SEND_SPI8_BURST= 6
SEND_SPI16_BURST= 7
#/*------I2C-------*/
I2C_HEADER= 4
I2C_START =1
I2C_SEND =2
I2C_STOP =3
I2C_RESTART =4
I2C_READ_END =5
I2C_READ_MORE =6
I2C_WAIT =7
I2C_SEND_BURST =8
I2C_CONFIG = 9
I2C_STATUS = 10

#/*------UART2--------*/
UART_2= 5
SEND_CHAR =1
SEND_INT= 2
SEND_ADDRESS= 3
SET_BAUD= 4
SET_MODE= 5

#/*-----------DAC--------*/
DAC =6
SET_DAC= 1
SET_PVS2 =2
SET_PVS3= 3
SET_PCS =4


#/*--------WAVEGEN-----*/
WAVEGEN =7
SET_WG1= 2
SET_WG2= 1
SET_SQR1 = 3
SET_SQR2 = 4
SET_SQRS = 5
TUNE_SINE_OSCILLATOR = 6
SQR4	=7
MAP_REFERENCE = 8
SET_BOTH_WG = 9
SET_WAVEFORM_TYPE = 10
SELECT_FREQ_REGISTER = 11
DELAY_GENERATOR = 12
#/*-----digital outputs----*/
DOUT= 8
SET_STATE = 1

#/*-----digital inputs-----*/
DIN  = 9
GET_STATE = 1
GET_STATES = 2


ID1	 = 0
ID2  = 1
ID3  = 2
ID4  = 3
LMETER = 4


#/*------TIMING FUNCTIONS-----*/
TIMING =10
GET_TIMING = 1
GET_PULSE_TIME=2
GET_DUTY_CYCLE=3
START_ONE_CHAN_LA =4
START_TWO_CHAN_LA =5
START_FOUR_CHAN_LA =6
FETCH_DMA_DATA =7
FETCH_INT_DMA_DATA =8
FETCH_LONG_DMA_DATA =9
GET_LA_PROGRESS =10
GET_INITIAL_DIGITAL_STATES = 11

TIMING_MEASUREMENTS=12
INTERVAL_MEASUREMENTS=13
CONFIGURE_COMPARATOR =14
START_ALTERNATE_ONE_CHAN_LA =15
START_THREE_CHAN_LA =16

#/*--------MISCELLANEOUS------*/
COMMON =11

GET_CTMU_VOLTAGE =1
GET_CAPACITANCE= 2
GET_FREQUENCY   =3
GET_INDUCTANCE  =4

GET_VERSION = 5

RETRIEVE_BUFFER     =8
GET_HIGH_FREQUENCY   =9
CLEAR_BUFFER		=10
SET_RGB				=11
READ_PROGRAM_ADDRESS		=12
WRITE_PROGRAM_ADDRESS		=13
READ_DATA_ADDRESS			=14
WRITE_DATA_ADDRESS			=15

GET_CAP_RANGE		=16
SET_ONBOARD_RGB		=17
#/*---------- BAUDRATE for main comm channel----*/
SETBAUD				=12
BAUD9600			=1
BAUD14400			=2
BAUD19200			=3
BAUD28800			=4
BAUD38400			=5
BAUD57600			=6
BAUD115200			=7
BAUD230400			=8
BAUD1000000			=9
#/*-----------NRFL01 radio module----------*/
NRFL01  =13
NRF_SETUP =1
NRF_RXMODE =2
NRF_TXMODE =3
NRF_POWER_DOWN =4
NRF_RXCHAR =5
NRF_TXCHAR =6
NRF_HASDATA =7
NRF_FLUSH =8
NRF_WRITEREG =9
NRF_READREG =10
NRF_GETSTATUS =11
NRF_WRITECOMMAND =12
NRF_WRITEPAYLOAD =13
NRF_READPAYLOAD =14
NRF_WRITEADDRESS=15
NRF_TRANSACTION = 16
#---------Non standard IO protocols--------

NONSTANDARD_IO = 14
HX711_HEADER = 1
HCSR04_HEADER = 2
AM2302_HEADER = 3
TCD1304_HEADER = 4
#--------COMMUNICATION PASSTHROUGHS--------
#Data sent to the device is directly routed to output ports such as (SCL, SDA for UART)

PASSTHROUGHS = 15
PASS_UART = 1

#/*--------STOP STREAMING------*/
STOP_STREAMING =253

#/*------INPUT CAPTURE---------*/
#capture modes
EVERY_SIXTEENTH_RISING_EDGE = 0b101
EVERY_FOURTH_RISING_EDGE    = 0b100
EVERY_RISING_EDGE           = 0b011
EVERY_FALLING_EDGE          = 0b010
EVERY_EDGE                  = 0b001
DISABLED		    = 0b000
#/*--------Chip selects-----------*/
CSA1	=1
CSA2	=2
CSA3	=3
CSA4	=4
CSA5	=5
CS1		=6
CS2		=7

#resolutions
TEN_BIT=10
TWELVE_BIT=12

def InttoString(val):
	return	chr(val&0xff) +  chr((val>>8)&0xff)

def StringtoInt(string):
	return	ord(string[0]) |  (ord(string[1])<<8)

def StringtoLong(string):
	return	ord(string[0]) |  (ord(string[1])<<8) |  (ord(string[2])<<16) |  (ord(string[3])<<24)

def getval12(val):
	return val*3.3/4095

def getval10(val):
	return val*3.3/1023


import math

def getL(F,C):
	return 1.0/(C*4*math.pi*math.pi*F*F)

def getF(L,C):
	return 1.0/(2*math.pi*math.sqrt(L*C))

def getLx(f1,f2,f3,Ccal):
	a=(f1/f3)**2
	b=(f1/f2)**2
	c=(2*math.pi*f1)**2
	return (a-1)*(b-1)/(Ccal*c)
	

def PR2(T,multiplier,postscaler):
	table_size=180
	return (T*8e6*multiplier)/(table_size*(1+postscaler))

def getfreq(pr2,m,p):
	table_size=180
	return (8e6*m)/(round(pr2)*table_size*(p+1))

def get_wave_parameters(freq):
	T=1.0/freq
	m=1;p=0
	#print 'initial guess',closest,a
	while 1:
		pr2=PR2(T,m,p)
		a=[int(round(pr2)),m,p]
		closest = getfreq(pr2,m,p)
		if pr2<40 and m<5:
			m+=1
			if(m==3):m=4
		elif pr2>255 and p<16:
			p+=1
		else:
			break
		
	if a[0]<40 or a[0]>255:
		print 'failed. not in range'
		success=False
	else:
		print 'final parameters', closest,a
		success=True
	return success,closest,a


def reverse_bits(x):
	return int('{:08b}'.format(x)[::-1], 2)


class Printer():
    """
    Print things to stdout on one line dynamically
    """
 
    def __init__(self,data):
 
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

