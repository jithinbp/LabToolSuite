import Labtools.interface as interface
import time
from numpy import int16

class HMC5883L:
	def __init__(self,ADDRESS=0x1E):
		self.ADDRESS = ADDRESS
		self.I = interface.Interface()

	def connect(self):
		self.I.I2C.start(self.ADDRESS,0) #writing mode
		self.I.I2C.send(0x01) #gain
		self.I.I2C.send(0<<5) #smallest range
		self.I.I2C.stop()


		self.I.I2C.start(self.ADDRESS,0) #writing mode
		self.I.I2C.send(0x02) #Mode
		self.I.I2C.send(0)    #Continuous measurement
		self.I.I2C.stop()
	
	def __getVals__(self,addr,bytes):
		self.I.I2C.start(self.ADDRESS,0)
		self.I.I2C.send(addr) #read raw values starting from address
		self.I.I2C.restart(self.ADDRESS,1)
		vals=self.I.I2C.read(bytes)
		self.I.I2C.stop()
		return vals

	def read(self):
		vals=self.__getVals__(0x03,6)
		x=int16((vals[0]<<8)|vals[1])	#conversion to signed datatype
		y=int16((vals[2]<<8)|vals[3])
		z=int16((vals[4]<<8)|vals[5])
		return x,y,z


'''		
a=HMC5883L()
a.connect()
while 1:
	print a.read()
'''	
