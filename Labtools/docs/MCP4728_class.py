from commands_proto import *
import I2C_class

class MCP4728:
	defaultVDD =3300
	RESET =6
	WAKEUP =9
	UPDATE =8
	WRITEALL =64
	WRITEONE =88
	SEQWRITE =80
	VREFWRITE =128
	GAINWRITE =192
	POWERDOWNWRITE =160
	GENERALCALL =0
	#def __init__(self,I2C,vref=3.3,devid=0):
	def __init__(self,H,vref=3.3,devid=0):
		self.devid = devid
		self.addr = 0x60|self.devid		#0x60 is the base address
		self.H=H
		self.I2C = I2C_class.I2C(self.H)
		self.SWITCHEDOFF=[0,0,0,0]
		self.VREFS=[0,0,0,0]  #0=Vdd,1=Internal reference
		self.VRANGES=[[0,3.3],[0,3.3],[-3.3,3.3],[-5,5]]

	def setVoltage(self,chan,v):
		R=self.VRANGES[chan]
		v = int(4095*(v-R[0])/(R[1]-R[0]))
		self.__setRawVoltage__(chan,v)
		return (R[1]-R[0])*v/4095+R[0]

	def __setRawVoltage__(self,chan,v):
		'''
		self.I2C.start(self.addr,0)
		self.I2C.send(self.WRITEONE | (chan << 1))
		self.I2C.send(self.VREFS[chan] << 7 | self.SWITCHEDOFF[chan] << 5 | 1 << 4 | (v>>8)&0xF )
		self.I2C.send(v&0xFF)
		self.I2C.stop()
		'''
		self.H.__sendByte__(DAC) #DAC write coming through.(MCP4922)
		self.H.__sendByte__(SET_DAC)
		self.H.__sendByte__(self.addr<<1)	#I2C address
		self.H.__sendByte__(chan)		#DAC channel
		self.H.__sendInt__((self.VREFS[chan] << 15) | (self.SWITCHEDOFF[chan] << 13) | (1 << 12) | v )
		#print chan,hex((self.VREFS[chan] << 15) | (self.SWITCHEDOFF[chan] << 13) | (1 << 12) | v )
		self.H.__get_ack__()
		R=self.VRANGES[chan]
		return (R[1]-R[0])*v/4095.+R[0]

	def __writeall__(self,v1,v2,v3,v4):
		self.I2C.start(self.addr,0)
		self.I2C.send((v1>>8)&0xF )
		self.I2C.send(v1&0xFF)
		self.I2C.send((v2>>8)&0xF )
		self.I2C.send(v2&0xFF)
		self.I2C.send((v3>>8)&0xF )
		self.I2C.send(v3&0xFF)
		self.I2C.send((v4>>8)&0xF )
		self.I2C.send(v4&0xFF)
		self.I2C.stop()

	def stat(self):
		self.I2C.start(self.addr,0)
		self.I2C.send(0x0) #read raw values starting from address
		self.I2C.restart(self.addr,1)
		vals=self.I2C.read(24)
		self.I2C.stop()
		print vals


