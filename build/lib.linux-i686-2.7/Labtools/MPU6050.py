import numpy as np

class KalmanFilter(object):
	'''
	Credits:http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
	'''
	def __init__(self, process_variance, estimated_measurement_variance):
		self.process_variance = process_variance
		self.estimated_measurement_variance = estimated_measurement_variance
		self.posteri_estimate = 0.0
		self.posteri_error_estimate = 1.0

	def input_latest_noisy_measurement(self, measurement):
		priori_estimate = self.posteri_estimate
		priori_error_estimate = self.posteri_error_estimate + self.process_variance

		blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
		self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
		self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

	def get_latest_estimated_measurement(self):
		return self.posteri_estimate

class ComplementaryFilter:
	def __init__(self,):
		self.pitch=0
		self.roll=0
		self.dt=0.001

	def addData(self,accData,gyrData):
		self.pitch += (gyrData[0]) * self.dt	# Angle around the X-axis
		self.roll -= (gyrData[1]) * self.dt	#Angle around the Y-axis
		forceMagnitudeApprox = abs(accData[0]) + abs(accData[1]) + abs(accData[2]);
		pitchAcc = np.arctan2(accData[1], accData[2]) * 180 / np.pi
		self.pitch = self.pitch * 0.98 + pitchAcc * 0.02
		rollAcc = np.arctan2(accData[0], accData[2]) * 180 / np.pi
		self.roll = self.roll * 0.98 + rollAcc * 0.02

	def getData(self):
		return self.roll,self.pitch

class MPU6050():
	def __init__(self,I):
		self.I=I
		self.ADDRESS = 0x68
		self.I.I2C.config(40000)
		self.I.I2C.start(self.ADDRESS,0) #writing mode
		self.I.I2C.send(0x6B) #power management
		self.I.I2C.send(0)
		self.I.I2C.stop()

	def getVals(self,addr,bytes):
		self.I.I2C.restart(self.ADDRESS,0)
		self.I.I2C.send(addr) #read raw values starting from 0x3B
		self.I.I2C.restart(self.ADDRESS,1)
		vals=self.I.I2C.read(bytes)
		self.I.I2C.stop()
		return vals

	def getRaw(self):
		vals=self.getVals(0x3B,14)
		ax=np.int16(vals[0]<<8|vals[1])
		ay=np.int16(vals[2]<<8|vals[3])
		az=np.int16(vals[4]<<8|vals[5])

		temp=np.int16(vals[6]<<8|vals[7])
	
		gx=np.int16(vals[8]<<8|vals[9])
		gy=np.int16(vals[10]<<8|vals[11])
		gz=np.int16(vals[12]<<8|vals[13])
		return [ax/65535.,ay/65535.,az/65535.,temp/65535.,gx/65535.,gy/65535.,gz/65535.]

	def getAccel(self):
		vals=self.getVals(0x3B,6)
		ax=np.int16(vals[0]<<8|vals[1])
		ay=np.int16(vals[2]<<8|vals[3])
		az=np.int16(vals[4]<<8|vals[5])
		return [ax/65535.,ay/65535.,az/65535.]

	def getTemp(self):
		vals=self.getVals(0x41,6)
		t=np.int16(vals[0]<<8|vals[1])
		return t/65535.

	def getGyro(self):
		vals=self.getVals(0x43,6)
		ax=np.int16(vals[0]<<8|vals[1])
		ay=np.int16(vals[2]<<8|vals[3])
		az=np.int16(vals[4]<<8|vals[5])
		return [ax/65535.,ay/65535.,az/65535.]
		
