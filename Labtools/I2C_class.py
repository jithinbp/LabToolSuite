from commands_proto import *

class I2C():
	"""
	Methods to interact with the I2C port. An instance of Labtools.Packet_Handler must be passed to the init function
	
	
	Example::  Read Values from an HMC5883L 3-axis Magnetometer(compass) [GY-273 sensor] connected to the I2C port
		>>> ADDRESS = 0x1E
		>>> from Labtools import interface
		>>> I = interface.Interface() 
		>>> # Alternately, you may skip using I2C as a child instance of Interface, 
		>>> # and instead use I2C=Labtools.I2C_class.I2C(Labtools.packet_handler.Handler())
		
		>>> I.I2C.start(self.ADDRESS,0) # writing to device mode
		>>> I.I2C.send(0x01) # Set gain of the magnetometer
		>>> I.I2C.send(0<<5) # Select the smallest range
		>>> I.I2C.stop()     #Stop the transfer


		>>> I.I2C.start(self.ADDRESS,0) # writing to device again
		>>> I.I2C.send(0x02) # Select Mode configuration register to write to
		>>> I.I2C.send(0)    # Select Continuous measurement mode
		>>> I.I2C.stop()
	
		>>> I.I2C.start(self.ADDRESS,0)	# writing to device
		>>> I.I2C.send(addr) # Write address to read raw values starting that location.
		>>> I.I2C.restart(self.ADDRESS,1) #Re write ADDRESS to I2C port, but in reading mode.
		>>> vals=I.I2C.read(6) #Read 6 bytes. 5 bytes with ack, and one with Nack (No acknowledge)
		>>> I.I2C.stop()
		
		>>> from numpy import int16
		>>> x=int16((vals[0]<<8)|vals[1])	#conversion to signed datatype
		>>> y=int16((vals[2]<<8)|vals[3])
		>>> z=int16((vals[4]<<8)|vals[5])
		>>> print x,y,z

	
	
	
	"""

	def __init__(self,H):
		self.H = H
		from Labtools import sensorlist
		self.SENSORS=sensorlist.sensors

	def config(self,freq):
		"""
		Sets frequency for I2C transactions
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		freq			I2C frequency
		================	============================================================================================
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_CONFIG)
		#freq=1/((BRGVAL+1.0)/64e6+1.0/1e7)
		BRGVAL=int( (1./freq-1./1e7)*64e6-1 )
		self.H.__sendInt__(BRGVAL) 
		self.H.__get_ack__()

	def start(self,address,rw):
		"""
		Initiates I2C transfer to address via the I2C port
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		address				I2C slave address
		rw					Read/write.
							* 0 for writing
							* 1 for reading.
		================	============================================================================================
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_START)
		self.H.__sendByte__(((address<<1)|rw)&0xFF) # address
		return self.H.__get_ack__()>>4

	def stop(self):
		"""
		stops I2C transfer
		
		:return: Nothing
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_STOP)
		self.H.__get_ack__()

	def wait(self):
		"""
		wait for I2C

		:return: Nothing
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_WAIT)
		self.H.__get_ack__()

	def send(self,data):
		"""
		SENDS data over I2C.
		The I2C bus needs to be initialized and set to the correct slave address first.
		Use I2C.start(address) for this.
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		data				Sends data byte over I2C bus
		================	============================================================================================

		:return: Nothing
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_SEND)
		self.H.__sendByte__(data)		 #data byte
		return self.H.__get_ack__()>>4
		
	def send_burst(self,data):
		"""
		SENDS data over I2C. The function does not wait for the I2C to finish before returning.
		It is used for sending large packets quickly.
		The I2C bus needs to be initialized and set to the correct slave address first.
		Use start(address) for this.

		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		data				Sends data byte over I2C bus
		================	============================================================================================

		:return: Nothing
		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_SEND_BURST)
		self.H.__sendByte__(data)		 #data byte
		#No handshake. for the sake of speed. e.g. loading a frame buffer onto an I2C display such as ssd1306

	def restart(self,address,rw):
		"""
		Initiates I2C transfer to address

		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		address				I2C slave address
		rw					Read/write.
							* 0 for writing
							* 1 for reading.
		================	============================================================================================

		"""
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_RESTART)
		self.H.__sendByte__(((address<<1)|rw)&0xFF) # address
		return self.H.__get_ack__()>>4

	def read(self,length):
		"""
		Reads a fixed number of data bytes from I2C device. Fetches length-1 bytes with acknowledge bits for each, +1 byte
		with Nack.

		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		length				number of bytes to read from I2C bus
		================	============================================================================================
		"""
		data=[]
		for a in range(length-1):
			self.H.__sendByte__(I2C_HEADER)
			self.H.__sendByte__(I2C_READ_MORE)
			data.append(self.H.__getByte__())
			self.H.__get_ack__()
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_READ_END)
		data.append(self.H.__getByte__())
		self.H.__get_ack__()
		return data

	def read_repeat(self):
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_READ_MORE)
		val=self.H.__getByte__()
		self.H.__get_ack__()
		return val

	def read_end(self):
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_READ_END)
		val=self.H.__getByte__()
		self.H.__get_ack__()
		return val


	def read_status(self):
		self.H.__sendByte__(I2C_HEADER)
		self.H.__sendByte__(I2C_STATUS)
		val=self.H.__getInt__()
		self.H.__get_ack__()
		return val


	def scan(self,frequency = 100000):
		self.config(frequency)
		addrs=[]
		n=0
		print 'Scanning addresses 0-127...'
		print 'Address','\t','Possible Devices'
		for a in range(0,128):
			x = self.start(a,0)
			if x&1 == 0:	#ACK received
				addrs.append(a)
				print hex(a),'\t\t',self.SENSORS.get(a,'None')
				n+=1
			self.stop()
		return addrs






