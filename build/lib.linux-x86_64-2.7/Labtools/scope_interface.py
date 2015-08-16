import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from commands_proto import *

import packet_handler
import I2C_class,SPI_class,NRF24L01_class

from achan import *
from digital_channel import *
import serial,string,fcntl
import time
import sys

import numpy as np
import math

class Interface():
	"""
	**Communications library.**

	This class contains methods that can be used to interact with the hardware.

	Initialization does the following
	
	* connects to tty device
	* loads calibration values.

	+----------+-----------------------------------------------------------------+
	|Arguments |Description                                                      |
	+==========+=================================================================+
	|timeout   | serial port read timeout. default = 1s                          |
	+----------+-----------------------------------------------------------------+

	>>> from Labtools import interface
	>>> I = interface.Interface(2.0)
	>>> print I
	<interface.Interface instance at 0xb6c0cac>


	Once you have instantiated this class,  its various methods will allow access to all the features built
	into the device.
	
	
	"""

	def __init__(self,timeout=1.0,**kwargs):
		self.BAUD = 1000000
		self.timebase = 40
		self.MAX_SAMPLES = 3200
		self.samples=self.MAX_SAMPLES
		self.triggerLevel=550
		self.triggerChannel = 0
		self.error_count=0
		self.channels_in_buffer=0
		self.digital_channels_in_buffer=0
		
		#-------------get rid of these=-------
		self.CH1	= 3
		self.CH2	= 0
		self.CH3	= 1
		self.CH4	= 2
		self.CH5	 = 4
		self.IN1	 = 5
		self.IN2	 = 6
		self.SEN	 = 7
		self.PCS	 = 8
		self.ID1	 = 0
		self.ID2  = 1
		self.ID3  = 2
		self.ID4  = 3
		self.OD1=0
		self.OD2=1
		self.LOW=0
		self.HIGH=1
		self.LMETER = 4
		#-------------get rid of the above=-------

		self.digital_channel_names=['ID1','ID2','ID3','ID4','LMETER','CH4']
		self.dchans=[digital_channel(a) for a in range(4)]
		#This array of four instances of digital_channel is used to store data retrieved from the
		#logic analyzer section of the device.  It also contains methods to generate plottable data
		#from the original timestamp arrays.
		
		self.streaming=False
		self.achans=[analog_channel(a) for a in ['CH1','CH2','CH3','CH4']]
		self.pga_chip_select_map = {'CH1':1,'CH2':2,'CH3':3,'CH4':4,'CH5':5,'CH6':5,'CH7':5,'CH8':5,'CH9':5,'5V':5,'PCS':5,'9V':5}
		self.analog_gains={'CH1':0,'CH2':0,'CH3':0,'CH4':0}
		self.sensor_list = ['CH5','CH6','CH7','CH8','CH9','5V','PCS','9V']
		self.sensor_gain=0
		self.analog_channel_names=['CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9','5V','PCS','9V','IN1','SEN','TEMP']
		self.gain_values=[1,2,4,5,8,10,16,32]
		self.sensor_multiplex_channel=0
		self.sensor_multiplex_gain=0
		self.buff=np.zeros(4000)

		#--------------------------Initialize communication handler, and subclasses-----------------
		self.H = packet_handler.Handler(**kwargs)
		
		self.I2C = I2C_class.I2C(self.H)
		"""
		Sub-Instance I2C of the Interface library contains methods to access devices
		connected to the I2C port.
		
		example::
			>>> I.I2C.start(self.ADDRESS,0) #writing mode
			>>> I.I2C.send(0x01)
			>>> I.I2C.stop()
		
		.. seealso::  :py:meth:`~I2C_class.I2C` for complete documentation
		"""
		
		self.SPI = SPI_class.SPI(self.H)
		"""
		Sub-Instance SPI of the Interface library contains methods to access devices
		connected to the SPI port.
		
		example::
			>>> I=Interface()
			>>> I.SPI.start('CS1')
			>>> I.SPI.send16(0xAAFF)
			>>> print I.SPI.send16(0xFFFF)
			some number
		
		.. seealso:: :py:meth:`~SPI_class.SPI` for complete documentation
		"""
		self.NRF = NRF24L01_class.NRF24L01(self.H)

		self.DDS_MAX_FREQ = 0xFFFFFFFL-1	#24 bit resolution
		self.DDS_CLOCK = 1e6			#1 MHz clock
		self.map_reference_clock(7,'wavegen')
		print self.DDS_CLOCK

		for a in ['CH1','CH2','CH3','CH4','CH5']: self.set_gain(a,0)
		time.sleep(0.01)


	
	def __del__(self):
		print 'closing port'
		#try:self.fd.close()
		#except: pass
	#-------------------------------------------------------------------------------------------------------------------#

	#|================================================ANALOG SECTION====================================================|
	#|This section has commands related to analog measurement and control. These include the oscilloscope routines,     |
	#|voltmeters, ammeters, and Programmable voltage sources.							    |
	#-------------------------------------------------------------------------------------------------------------------#


	def capture1(self,ch,ns,tg):
		"""
		Blocking call that fetches an oscilloscope trace from the specified input channel
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		ch		Channel to select as input. ['CH1'..'CH9','5V','PCS','9V','IN1','SEN']
		ns		Number of samples to fetch. Maximum 3200
		tg		Timegap between samples in microseconds
		==============	============================================================================================

		.. figure:: ../images/capture1.png
			:width: 400px
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			A sine wave captured and plotted.
		
		Example
		
		>>> from pylab import *
		>>> from Labtools import interface
		>>> I=interface.Interface()
		>>> x,y = I.capture1('CH1',3200,1)
		>>> plot(x,y)
		>>> show()
				
		
		:return: Arrays X(timestamps),Y(Corresponding Voltage values)
		
		"""
		self.capture_traces(1,ns,tg,ch)
		time.sleep(1e-6*self.samples*self.timebase+.01)
		while not self.oscilloscope_progress()[0]:
			pass
		return self.fetch_trace(1)

	def capture2(self,ns,tg):
		"""
		Blocking call that fetches oscilloscope traces from CH1,CH2
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		ns				Number of samples to fetch. Maximum 1600
		tg				Timegap between samples in microseconds
		==============	============================================================================================

		.. figure:: ../images/capture2.png
			:width: 400px
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			Two sine waves captured and plotted.

		Example	
	
		>>> from pylab import *
		>>> from Labtools import interface
		>>> I=interface.Interface()
		>>> x,y1,y2 = I.capture2(1600,1.25)
		>>> plot(x,y1)				
		>>> plot(x,y2)				
		>>> show()				
		
		:return: Arrays X(timestamps),Y1(Voltage at CH1),Y2(Voltage at CH2)
		
		"""
		self.capture_traces(2,ns,tg)
		time.sleep(1e-6*self.samples*self.timebase+.01)
		while not self.oscilloscope_progress()[0]:
			pass
		x,y=self.fetch_trace(1)
		x,y2=self.fetch_trace(2)
		return x,y,y2		

	def capture4(self,ns,tg):
		"""
		Blocking call that fetches oscilloscope traces from CH1,CH2,CH3,CH4
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		ns				Number of samples to fetch. Maximum 800
		tg				Timegap between samples in microseconds. Minimum 1.75uS
		==============	============================================================================================

		.. figure:: ../images/capture4.png
			:width: 400px
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			Four traces captured and plotted.
	
		Example
	
		>>> from pylab import *
		>>> I=interface.Interface()
		>>> x,y1,y2,y3,y4 = I.capture4(800,1.75)
		>>> plot(x,y1)				
		>>> plot(x,y2)				
		>>> plot(x,y3)				
		>>> plot(x,y4)				
		>>> show()				
		
		:return: Arrays X(timestamps),Y1(Voltage at CH1),Y2(Voltage at CH2),Y3(Voltage at CH3),Y4(Voltage at CH4)
		
		"""
		self.capture_traces(4,ns,tg)
		time.sleep(1e-6*self.samples*self.timebase+.01)
		while not self.oscilloscope_progress()[0]:
			pass
		x,y=self.fetch_trace(1)
		x,y2=self.fetch_trace(2)
		x,y3=self.fetch_trace(3)
		x,y4=self.fetch_trace(4)
		return x,y,y2,y3,y4		

	def capture_traces(self,num,samples,tg,channel_one_input='CH1',CH123SA=0,**kwargs):
		"""
		Instruct the ADC to start sampling. use fetch_trace to retrieve the data

		===================	============================================================================================
		**Arguments** 
		===================	============================================================================================
		num		   	Channels to acquire. 1/2/4
		samples		   	Total points to store per channel. Maximum 3200 total.
		tg		   	Timegap between two successive samples (in uSec)
		channel_one_input 	map channel 1 to 'CH1' ... 'CH9'
		\*\*kwargs        
		
		* trigger	   	Whether or not to trigger the oscilloscope based on the voltage level set by :func:`configure_trigger`
		===================	============================================================================================

		.. figure:: ../images/transient.png
			:width: 600px
			:align: center
			:alt: alternate text
			:figclass: align-center
			
			Transient response of an Inductor and Capacitor in series
	
		.. _adc_example:

			The following example demonstrates how to use this function to record active events.

				* Connect a capacitor and an Inductor in series.
				* Connect CH1 to the spare leg of the inductor. Also Connect OD1 to this point
				* Connect CH2 to the junction between the capacitor and the inductor
				* connect the spare leg of the capacitor to GND( ground )
				* set OD1 initially high using set_state(OD1=1)
				
			>>> I.set_state(OD1=1)	#Turn on OD1
			>>> time.sleep(0.5)     #Arbitrary delay to wait for stabilization
			
			>>> I.capture_traces(2,800,2,trigger=False)	#Start acquiring data (2 channels,800 samples, 2microsecond intervals)
			>>> I.set_state(OD1=0)	#Turn off OD1. This must occur immediately after the previous line was executed.
			>>> time.sleep(800*2*1e-6)	#Minimum interval to wait for completion of data acquisition. samples*timegap*(convert to Seconds)
			>>> x,CH1=I.fetch_trace(1)
			>>> x,CH2=I.fetch_trace(2)
			>>> plot(x,CH1-CH2)	#Voltage across the inductor				
			>>> plot(x,CH2)		##Voltage across the capacitor		
			>>> show()				
	
			The following events take place when the above snippet runs
	
			#. The oscilloscope starts storing voltages present at CH1 and CH2 every 2 microseconds
			#. The output OD1 was enabled, and this causes the voltages across the L and C to fluctuate
			#. The data from CH1 and CH2 was read into x,CH1,CH2
			#. Both traces were plotted in order to visualize the Transient response of series LC
		
		:return: nothing
		
		.. seealso::
			
			:func:`fetch_trace` , :func:`oscilloscope_progress` , :func:`capture1` , :func:`capture2` , :func:`capture4`
	
		"""
		triggerornot=0x80 if kwargs.get('trigger',True) else 0
		self.timebase=tg
		self.H.__sendByte__(ADC)
		if channel_one_input in self.analog_gains:
			self.achans[0].gain = self.analog_gains[channel_one_input]
		elif channel_one_input in self.sensor_list:
			self.achans[0].gain = self.sensor_gain
		else:
			self.achans[0].gain = 0
		self.achans[1].gain = self.analog_gains['CH2']
		self.achans[2].gain = self.analog_gains['CH3']
		self.achans[3].gain = self.analog_gains['CH4']
		CHOSA = self.__calcCHOSA__(channel_one_input)
		if(num==1):
			if(self.timebase<1):self.timebase=1.0
			if(samples>self.MAX_SAMPLES):samples=self.MAX_SAMPLES

			self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase)

			self.H.__sendByte__(CAPTURE_ONE)			#read 1 channel
			self.H.__sendByte__(CHOSA|triggerornot)		#channelk number

		elif(num==2):
			if(self.timebase<1.25):self.timebase=1.25
			if(samples>self.MAX_SAMPLES/2):samples=self.MAX_SAMPLES/2

			self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase)
			self.achans[1].set_params(channel='CH2',length=samples,timebase=self.timebase)
			
			self.H.__sendByte__(CAPTURE_TWO)			#ccapture 2 channels
			self.H.__sendByte__(CHOSA|triggerornot)				#channel 0 number


		elif(num==3 or num==4):
			if(self.timebase<1.75):self.timebase=1.75
			if(samples>self.MAX_SAMPLES/4):samples=self.MAX_SAMPLES/4
			self.achans[0].set_params(channel=channel_one_input,length=samples,timebase=self.timebase)
			for a in range(1,4):
				self.achans[a].set_params(channel=['NONE','CH2','CH3','CH4'][a],length=samples,timebase=self.timebase)
			
			self.H.__sendByte__(CAPTURE_FOUR)			#read 4 channels
			self.H.__sendByte__(CHOSA|(CH123SA<<4)|triggerornot)		#channel number

		self.samples=samples
		self.H.__sendInt__(samples)			#number of samples to read
		self.H.__sendInt__(int(self.timebase*8))		#Timegap between samples.  8MHz timer clock
		self.H.__get_ack__()
		self.channels_in_buffer=num
	
	def fetch_trace(self,channel_number):
		"""
		fetches a channel(1-4) captured by :func:`capture_traces` called prior to this, and returns xaxis,yaxis

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel_number	Any of the maximum of four channels that the oscilloscope captured. 1/2/3/4
 		==============	============================================================================================

		:return: time array,voltage array

		.. seealso::
			
			:func:`capture_traces` , :func:`oscilloscope_progress`

		"""
		self.__fetch_channel__(channel_number)
		return self.achans[channel_number-1].get_xaxis(),self.achans[channel_number-1].get_yaxis()
		
	def oscilloscope_progress(self):
		"""
		returns the number of samples acquired by the capture routines, and the conversion_done status
		
		:return: conversion done,samples acquired

		>>> I.start_capture(1,3200,2)
		>>> print I.oscilloscope_progress()
		(0,46)
		>>> time.sleep(3200*2e-6)
		>>> print I.oscilloscope_progress()
		(1,3200)
		
		.. seealso::
			
			:func:`fetch_trace` , :func:`capture_traces`

		"""
		conversion_done=0
		samples=0
		try:
			self.H.__sendByte__(ADC)
			self.H.__sendByte__(GET_CAPTURE_STATUS)
			conversion_done = self.H.__getByte__()
			samples = self.H.__getInt__()
			self.H.__get_ack__()
		except:
			print 'disconnected!!'
			#sys.exit(1)
		return conversion_done,samples

	def __fetch_channel__(self,channel_number):
		"""
		Fetches a section of data from any channel and stores it in the relevant instance of achan()
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel_number	channel number (1,2,3,4)
		==============	============================================================================================
		
		:return: True if successful
		"""
		samples = self.achans[channel_number-1].length
		if(channel_number>self.channels_in_buffer):
			print 'Channel unavailable'
			return False
		data=''
		splitting=20
		for i in range(int(samples/splitting)):
			self.H.__sendByte__(ADC)
			self.H.__sendByte__(GET_CAPTURE_CHANNEL)
			self.H.__sendByte__(channel_number-1)	#starts with A0 on PIC
			self.H.__sendInt__(splitting)
			self.H.__sendInt__(i*splitting)
			data+= self.H.fd.read(splitting*2)		#reading int by int sometimes causes a communication error. this works better.
			self.H.__get_ack__()

		self.H.__sendByte__(ADC)
		self.H.__sendByte__(GET_CAPTURE_CHANNEL)
		self.H.__sendByte__(channel_number-1)	#starts with A0 on PIC
		self.H.__sendInt__(samples%splitting)
		self.H.__sendInt__(samples-samples%splitting)
		data += self.H.fd.read(2*(samples%splitting)) 		#reading int by int sometimes causes a communication error. this works better.
		self.H.__get_ack__()

		for a in range(samples): self.buff[a] = ord(data[a*2])|(ord(data[a*2+1])<<8)
		self.achans[channel_number-1].yaxis = self.achans[channel_number-1].fix_value(self.buff[:samples])
		return True



	def __fetch_channel_oneshot__(self,channel_number):
		"""
		Fetches all data from given channel and stores it in the relevant instance of achan()
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel_number	channel number (1,2,3,4)
		==============	============================================================================================
		
		"""
		offset=0 
		samples = self.achans[channel_number-1].length
		if(channel_number>self.channels_in_buffer):
			print 'Channel unavailable'
			return False
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(GET_CAPTURE_CHANNEL)
		self.H.__sendByte__(channel_number-1)	#starts with A0 on PIC
		self.H.__sendInt__(samples)
		self.H.__sendInt__(offset)
		data = self.H.fd.read(samples*2)		#reading int by int sometimes causes a communication error. this works better.
		self.H.__get_ack__()
		for a in range(samples): self.buff[a] = ord(data[a*2])|(ord(data[a*2+1])<<8)
		self.achans[channel_number-1].yaxis = self.achans[channel_number-1].fix_value(self.buff[:samples])
		return True


		
	def configure_trigger(self,chan,level):
		"""
		configure trigger parameters for 10-bit capture commands
		The capture routines will wait till a rising edge of the input signal crosses the specified level.
		The trigger will timeout within 8mS, and capture routines will start regardless.
		
		These settings will not be used if the trigger option in the capture routines are set to False
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		chan			channel . 0,1,2 or 3 corresponding to the channels being recorded by the capture routines
		level			The voltage level that should trigger the capture sequence(in Volts)
		==============	============================================================================================

		**Example**
		
		>>> I.configure_trigger(0,1.1)
		>>> I.capture_traces(4,800,2)
		>>> I.fetch_trace(1)  #Unless a timeout occured, the first point of this channel will be close to 1.1Volts
		>>> I.fetch_trace(2)  #This channel was acquired simultaneously with channel 1, so it's triggered along with the first
		
		.. seealso::
			
			:func:`capture_traces` , adc_example_

		"""
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(CONFIGURE_TRIGGER)
		self.H.__sendByte__(1<<chan)	#Trigger channel
		level = 511-31*level*self.gain_values[self.achans[chan].gain]
		if level>1023:level=1023
		elif level<0:level=0
		self.H.__sendInt__(int(level))	#Trigger
		self.H.__get_ack__()

	
				
	def set_gain(self,channel,gain):
		"""
		set the gain of the selected PGA
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel			'CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9','5V','PCS','9V'
		gain			(0-7) -> (1x,2x,4x,5x,8x,10x,16x,32x)
		==============	============================================================================================
		
		.. note::
			The gain value applied to a channel will result in better resolution for small amplitude signals.
			
			However, values read using functions like :func:`get_average_voltage` or	:func:`capture_traces` 
			will not be 2x, or 4x times the input signal. These are calibrated to return accurate values of the original input signal.
		
		>>> I.set_gain('CH1',7)  #gain set to 32x on CH1

		"""
		if channel in self.pga_chip_select_map:
			chan = self.pga_chip_select_map[channel]
		else:
			print 'No amplifier exists on this channel :',channel
			return
		
		if channel in self.analog_gains:
			self.analog_gains[channel] = gain
		elif channel in self.sensor_list:
			self.sensor_gain = gain
		else:
			print "No such channel ",channel,"\n try 'CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9','5V','PCS','9V' "
			return
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(SET_PGA_GAIN)
		self.H.__sendByte__(chan) #send the channel
		self.H.__sendByte__(gain) #send the gain
		self.H.__get_ack__()
		return self.gain_values[gain]

	def write_dac(self,channel,n):
		"""
		writes a value(12 bit) to the DAC.

		+----------+-----------------------------------------------------------------+
		|Arguments |Description                                                      |
		+==========+=================================================================+
		|channel   | channel number.                                                 |
		+          +                                                                 +
		|          | * 0 -> PVS1 (-5 to 5V)                                          |
		+          +                                                                 +
		|          | * 1 -> PVS2 (0-3V)                                              |
		+----------+-----------------------------------------------------------------+
		|n         | value to set (0-4095)                                           |
		+----------+-----------------------------------------------------------------+
		
		:return: nothing

		.. warning:: n should be between 0 and 4095 for both channels. The output voltage will be scaled accordingly.

		>>> I.write_dac(0,4095) # pvs1 set to 5Volts
		>>> I.write_dac(0,4095) # pvs1 set to -5Volts
		
		.. seealso::
			
			:func:`set_pvs1` and :func:`set_pvs2`

				
		"""		
		self.H.__sendByte__(DAC) #DAC write coming through.(MCP4922)
		self.H.__sendByte__(SET_PVS1)
		val=(channel<<15)|(1<<14)|(1<<13)|(1<<12)|n #channel-15,buf-14,g-13,on/off-12,value 0-11
		self.H.__sendInt__(val)
		self.H.__get_ack__()

	def __selectSensorChannel__(self,channel):
		"""
		set the channel of PGA 5
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel			channel number. 0-7
		==============	============================================================================================
		
		"""
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(SELECT_PGA_CHANNEL)
		self.H.__sendByte__(channel) #send the channel
		self.H.__get_ack__()

	
	def __calcCHOSA__(self,name):
		bipolars=['CH2','CH3','CH4','CH1']
		unipolars=['CH5','CH6','CH7','CH8','CH9','5V','PCS','9V']
		others=['IN1','CHIP SELECT. IGNORE','SEN','TEMP']
		name=name.upper()
		if name in bipolars:
			return bipolars.index(name)
		elif name in unipolars:
			if self.sensor_multiplex_channel != unipolars.index(name):
				self.sensor_multiplex_channel = unipolars.index(name)
				self.__selectSensorChannel__(self.sensor_multiplex_channel)
			return 4
		elif name in others:
			return others.index(name)+5
		else:
			print 'not a valid channel name. selecting CH1'
			return 3
		
		
	def get_average_voltage(self,channel_name,sleep=0):
		""" 
		Return the voltage on the selected channel
		
		+------------+-----------------------------------------------------------------------------------------+
		|Arguments   |Description                                                                              |
		+============+=========================================================================================+
		|channel_name| 'CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9','5V','PCS','9V','IN1','SEN','TEMP'|
		+------------+-----------------------------------------------------------------------------------------+
		|sleep       | read voltage in CPU sleep mode. not particularly useful.                                |
		+------------+-----------------------------------------------------------------------------------------+

		Example:
		
		>>> print I.get_average_voltage('CH4')
		0.002
		
		"""
		chosa = self.__calcCHOSA__(channel_name)
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(GET_VOLTAGE_SUMMED)
		if(sleep):self.H.__sendByte__(chosa|0x80)#sleep mode conversion. buggy
		else:self.H.__sendByte__(chosa) 
		self.H.__getInt__() #2 Zeroes sent by UART. sleep or no sleep :p
		V_sum = self.H.__getInt__()
		#V = [self.H.__getInt__() for a in range(16)]
		#print V
		self.H.__get_ack__()
		V=1023*V_sum/16./4095
		if channel_name in self.analog_gains:
			gain = self.analog_gains[channel_name]
		elif channel_name in self.sensor_list:
			gain = self.sensor_gain
		else:
			gain = 0
		V=calfacs[channel_name][gain](V)
		return  V #sum(V)/16.0	#



	def __get_raw_average_voltage__(self,channel_name,sleep=0):
		""" 
		Return the average of 16 raw 10-bit ADC values of the voltage on the selected channel
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel_name    'CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9','5V','PCS','9V','IN1','SEN','TEMP'
		sleep		read voltage in CPU sleep mode. not particularly useful.
		==============	============================================================================================

		"""
		chosa = self.__calcCHOSA__(channel_name)
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(GET_VOLTAGE_SUMMED)
		if(sleep):self.H.__sendByte__(chosa|0x80)#sleep mode conversion. buggy
		else:self.H.__sendByte__(chosa) 
		self.H.__getInt__() #2 Zeroes sent by UART. sleep or no sleep :p
		V_sum = self.H.__getInt__()
		self.H.__get_ack__()
		V=1023*V_sum/16./4095
		return  V #sum(V)/16.0	#





	#-------------------------------------------------------------------------------------------------------------------#

	#|===============================================DIGITAL SECTION====================================================|	
	#|This section has commands related to digital measurement and control. These include the Logic Analyzer, frequency |
	#|measurement calls, timing routines, digital outputs etc							    |
	#-------------------------------------------------------------------------------------------------------------------#
	def __calcDChan__(self,name):
		"""
		accepts a string represention of a digital input ( 'ID1','ID2','ID3','ID4','LMETER','CH4' ) and returns a corresponding number
		"""
		
		if name in self.digital_channel_names:
			return self.digital_channel_names.index(name)
		else:
			print ' invalid channel',name,' , selecting ID1 instead '
			return 0
		
	def get_high_freq(self,pin):
		""" 
		retrieves the frequency of the signal connected to ID1. >10MHz
		also good for lower frequencies, but avoid using it since
		the ADC cannot be used simultaneously. It shares a TIMER with the ADC.
		
		The input frequency is fed to a 32 bit counter for a period of 100mS.
		The value of the counter at the end of 100mS is used to calculate the frequency.
		
		.. seealso:: :func:`get_freq`
		
		==============	============================================================================================
		**Arguments**
		==============	============================================================================================
		pin		The input pin to measure frequency from. 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
						
		==============	============================================================================================

		:return: frequency
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(GET_HIGH_FREQUENCY)
		self.H.__sendByte__(self.__calcDChan__(pin))
		scale=self.H.__getByte__()
		val = self.H.__getLong__()
		self.H.__get_ack__()
		return scale*(val)/1.0e-1 #100mS sampling

	def get_freq(self,channel='ID1',timeout=0.1):
		"""
		Frequency measurement on IDx.
		Measures time taken for 16 rising edges of input signal.
		returns the frequency in Hertz

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel		The input to measure frequency from. 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
		timeout		This is a blocking call which will wait for one full wavelength before returning the
				calculated frequency.
				Use the timeout option if you're unsure of the input signal.
				returns 0 if timed out
		==============	============================================================================================

		:return float: frequency
		
		
		.. _timing_example:
		
			* connect SQR1 to ID1
			
			>>> I.set_sqr1(2000,500,1) # TODO: edit this function
			>>> print I.get_freq('ID1')
			4000.0
			>>> print I.r2r_time('ID1')	#time between successive rising edges
			0.00025
			>>> print I.f2f_time('ID1') #time between successive falling edges
			0.00025
			>>> print I.pulse_time('ID1') #may detect a low pulse, or a high pulse. Whichever comes first
			6.25e-05
			>>> I.duty_cycle('ID1')		#returns wavelength, high time
			(0.00025,6.25e-05)			
		
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(GET_FREQUENCY)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__(self.__calcDChan__(channel))
		tmt = self.H.__getInt__()
		x=[self.H.__getLong__() for a in range(2)]
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return 0
		freq = lambda t: 16*64e6/t if(t) else 0
		y=x[1]-x[0]
		return freq(y)

	def r2r_time(self,channel='ID1',timeout=0.1):
		""" 
		Returns the time interval between two rising edges
		of input signal on ID1

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel		The input to measure time between two rising edges.'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
		timeout		Use the timeout option if you're unsure of the input signal time period.
				returns 0 if timed out
		==============	============================================================================================

		:return float: time between two rising edges of input signal
		
		.. seealso:: timing_example_

		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(GET_TIMING)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__( EVERY_RISING_EDGE<<2 | 2)
		self.H.__sendByte__(self.__calcDChan__(channel))
		tmt = self.H.__getInt__()
		x=[self.H.__getLong__() for a in range(2)]
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return -1
		rtime = lambda t: t/64e6
		y=x[1]-x[0]
		return rtime(y)

	def f2f_time(self,channel='ID1',timeout=0.1):
		""" 
		Returns the time interval between two falling edges
		of input signal on ID1

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel		The input to measure time between two falling edges. 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
		timeout		Use the timeout option if you're unsure of the input signal time period.
				returns 0 if timed out
		==============	============================================================================================

		:return float: time between two falling edges of input signal

		.. seealso:: timing_example_

		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(GET_TIMING)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__( EVERY_FALLING_EDGE<<2 | 2)
		self.H.__sendByte__(self.__calcDChan__(channel))

		tmt = self.H.__getInt__()
		x=[self.H.__getLong__() for a in range(2)]
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return -1
		rtime = lambda t: t/64e6
		y=x[1]-x[0]
		return rtime(y)

	def DutyCycle(self,channel='ID1',timeout=0.1):
		""" 
		duty cycle measurement on channel
		
		returns wavelength(seconds), and length of first half of pulse(high time)
		
		low time = (wavelength - high time)

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel		The input pin to measure wavelength and high time. 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
		timeout		Use the timeout option if you're unsure of the input signal time period.
				returns 0 if timed out
		==============	============================================================================================

		:return : wavelength,duty cycle

		.. seealso:: timing_example_

		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(GET_DUTY_CYCLE)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__(self.__calcDChan__(channel)|(self.__calcDChan__(channel)<<4))
		x=[self.H.__getLong__() for a in range(3)]
		edge = self.H.__getByte__()
		tmt = self.H.__getInt__()
		self.H.__get_ack__()
		if edge:   #rising edge has occurred
			y = [x[1]-x[0],x[2]-x[0]]
		else:		#falling edge
			y = [x[2]-x[1],x[2]-x[0]]
		print x,y,edge
		if(tmt >= timeout_msb):return -1,-1
		rtime = lambda t: t/64e6
		params = rtime(y[1]),rtime(y[0])/rtime(y[1])
		return params

	def MeasureInterval(self,channel1,channel2,edge1,edge2,timeout=0.1):
		""" 
		Measures time intervals between two logic level changes on any two digital inputs(both can be the same)

		For example, one can measure the time interval between the occurence of a rising edge on ID1, and a falling edge on ID3.
		If the returned time is negative, it simply means that the event corresponding to channel2 occurred first.
		
		returns the calculated time
		
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel1		The input pin to measure first logic level change
		channel1		The input pin to measure second logic level change
							* 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
							
		edge1			The type of level change to detect in order to start the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
							
		edge2			The type of level change to detect in order to stop the timer
							* 'rising'
							* 'falling'
							* 'four rising edges'
							
		timeout			Use the timeout option if you're unsure of the input signal time period.
					returns -1 if timed out
		==============	============================================================================================

		:return : time

		.. seealso:: timing_example_
		
		
		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(INTERVAL_MEASUREMENTS)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)

		self.H.__sendByte__(self.__calcDChan__(channel1)|(self.__calcDChan__(channel2)<<4))

		params =0
		if edge1  == 'rising': params |= 3 
		elif edge1=='falling': params |= 2
		else: 		       params |= 4

		if edge2  == 'rising': params |= 3<<3 
		elif edge2=='falling': params |= 2<<3
		else: 		       params |= 4<<3

		self.H.__sendByte__(params)
		A=self.H.__getLong__()
		B=self.H.__getLong__()
		tmt = self.H.__getInt__()
		self.H.__get_ack__()
		#print A,B
		if(tmt >= timeout_msb or B==0):return -1
		rtime = lambda t: t/64e6
		return rtime(B-A+20)

	def pulse_time(self,channel='CH1',timeout=0.1):
		""" 
		pulse time measurement on ID1
		returns pulse length(s) of high pulse or low pulse. whichever occurs first

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		channel			The input pin to measure pulse width from.
							* 'ID1' , 'ID2', 'ID3', 'ID4', 'LMETER','CH4'
		timeout			Use the timeout option if you're unsure of the input signal time period.
						returns 0 if timed out
		==============	============================================================================================

		:return float: pulse width in seconds

		.. seealso:: timing_example_

		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(GET_PULSE_TIME)
		timeout_msb = int((timeout*64e6))>>16
		self.H.__sendInt__(timeout_msb)
		self.H.__sendByte__(self.__calcDChan__(channel))
		x=[self.H.__getLong__() for a in range(2)]
		tmt = self.H.__getInt__()
		self.H.__get_ack__()
		if(tmt >= timeout_msb):return -1
		rtime = lambda t: t/64e6
		#print params[0]*1e6,params[1]*1e6
		return rtime(x[1]-x[0])

	def setup_comparator(self,level=7,digital_filter=3):
		""" 
		setup the voltage level and filtering on the analog comparator linked to CH4.
		It can then be used to directly estimate the frequency and other timing details of input analog waveforms on CH4

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		level			voltage level for + reference of comparator [0-15]

		digital_filter		Level changes faster than 3 * cpu freq / (1<<digital_filter) will be ignored
		==============	============================================================================================

		.. seealso:: timing_example_

		"""
		print (1./4)*(3.3) + (level/32.)*(3.3) 
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(CONFIGURE_COMPARATOR)
		self.H.__sendByte__(level | (digital_filter<<4) )
		self.H.__get_ack__()

	def LA_capture1(self,waiting_time=0.1,trigger=0):
		""" 
		log timestamps of rising/falling edges on one digital input (ID1)

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		waiting_time	   Total time to allow the logic analyzer to collect data.
				   This is implemented using a simple sleep routine, so if large delays will be involved,
				   refer to :func:`start_one_channel_LA` to start the acquisition, and :func:`fetch_LA_channels` to
				   retrieve data from the hardware after adequate time. The retrieved data is stored
				   in the array self.dchans[0].timestamps. Divide each timestamp by 64e6 to convert to seconds.
		trigger	           Edge trigger on ID1.
					options = 0  , 'rising' , 'falling'
		==============	============================================================================================
		
		:return: Bool initial_state Low/High, timestamp array in Seconds

		::

			>>> I.LA_capture1(0.2,'rising')
			
			
			
		"""
		if trigger!=0:
			if trigger not in ['rising','falling']:
				print 'Error. invalid value for trigger:',trigger,'\nTry trigger="rising"'
				return 0,[]
			self.start_one_channel_LA(True,'ID1',edge=trigger,trigger_channels=['ID1'])
		else:
			self.start_one_channel_LA(False,'ID1')
		time.sleep(waiting_time)

		data=self.get_LA_initial_states()
		tmp = self.fetch_long_data_from_LA(data[0],1)
		return data[4][0],tmp/64e6		



	def start_one_channel_LA(self,trigger=1,channel='ID1',maximum_time=67,**args):
		""" 
		start logging timestamps of rising/falling edges on ID1

		================== ======================================================================================================
		**Arguments** 
		================== ======================================================================================================
		trigger			Bool . Enable edge trigger on ID1. use keyword argument edge='rising' or 'falling'
		channel			'ID1',...'LMETER','CH4'
		maximum_time	   Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		kwargs
		triggger_channels  array of digital input names that can trigger the acquisition.eg. trigger= ['ID1','ID2','ID3']
					will triggger when a logic change specified by the keyword argument 'edge' occurs
					on either or the three specified trigger inputs.
		edge		   'rising' or 'falling' . trigger edge type for trigger_channels.
		================== ======================================================================================================
		
		:return: Nothing

		"""
		self.clear_buffer(0,self.MAX_SAMPLES/2);
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(START_ONE_CHAN_LA)
		self.H.__sendInt__(self.MAX_SAMPLES/4)
		#trigchan bit functions
			# b0 - trigger or not
			# b1 - trigger edge . 1 => rising. 0 => falling
			# b2, b3 - channel to acquire data from. ID1,ID2,ID3,ID4,COMPARATOR
			# b4 - trigger channel ID1
			# b5 - trigger channel ID2
			# b6 - trigger channel ID3

		if ('trigger_channels' in args) and trigger&1:
			trigchans = args.get('trigger_channels',0)
			if 'ID1' in trigchans : trigger|= (1<<4)
			if 'ID2' in trigchans : trigger|= (1<<5)
			if 'ID3' in trigchans : trigger|= (1<<6)
		else:
			trigger |= 1<<(self.__calcDChan__(channel)+4) #trigger on specified input channel if not trigger_channel argument provided

		trigger |= 2 if args.get('edge',0)=='rising' else 0
		trigger |= self.__calcDChan__(channel)<<2

		self.H.__sendByte__(trigger)
		self.H.__get_ack__()
		self.digital_channels_in_buffer = 1
		for a in self.dchans:
			a.prescaler = 0
			a.datatype='long'
			a.length = self.MAX_SAMPLES/4
			a.maximum_time = maximum_time*1e6 #conversion to uS
			a.mode = EVERY_EDGE


	def start_one_channel_LA1(self,**args):
		""" 
		start logging timestamps of rising/falling edges on ID1

		================== ======================================================================================================
		**Arguments** 
		================== ======================================================================================================
		kwargs
		channel			'ID1',...'LMETER','CH4'
		trigger_channel		'ID1',...'LMETER','CH4'

		channnel_mode		modes for each channel. Array with four elements
					default value: 1

					EVERY_SIXTEENTH_RISING_EDGE = 5
					EVERY_FOURTH_RISING_EDGE    = 4
					EVERY_RISING_EDGE           = 3
					EVERY_FALLING_EDGE          = 2
					EVERY_EDGE                  = 1
					DISABLED                    = 0
		
		trigger_mode		same as channel_mode.
					default_value : 3

		================== ======================================================================================================
		
		:return: Nothing

		"""
		self.clear_buffer(0,self.MAX_SAMPLES/2);
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(START_ALTERNATE_ONE_CHAN_LA)
		self.H.__sendInt__(self.MAX_SAMPLES/4)


		self.H.__sendByte__((self.__calcDChan__(args.get('channel','ID1'))<<4)|args.get('channel_mode',1))
		self.H.__sendByte__((self.__calcDChan__(args.get('trigger_channel','ID1'))<<4)|args.get('trigger_mode',3))

		self.H.__get_ack__()
		self.digital_channels_in_buffer = 1
		for a in self.dchans:
			a.prescaler = 0
			a.datatype='long'
			a.length = self.MAX_SAMPLES/4
			a.maximum_time = maximum_time*1e6 #conversion to uS
			a.mode = EVERY_EDGE




	def start_two_channel_LA(self,trigger=1,maximum_time=67):
		""" 
		start logging timestamps of rising/falling edges on ID1,AD2		
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		trigger			Bool . Enable rising edge trigger on ID1
		maximum_time	Total time to sample. If total time exceeds 67 seconds, a prescaler will be used in the reference clock
		==============	============================================================================================

		::

			"fetch_long_data_from_dma(points to read,1)" to get data acquired from channel 1
			"fetch_long_data_from_dma(points to read,2)" to get data acquired from channel 2
			The read data can be accessed from self.dchans[0 or 1]
		"""
		self.clear_buffer(0,self.MAX_SAMPLES);
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(START_TWO_CHAN_LA)
		self.H.__sendInt__(self.MAX_SAMPLES/4)
		self.H.__sendByte__(trigger)
		self.H.__get_ack__()
		for a in self.dchans:
			a.prescaler = 0
			a.length = self.MAX_SAMPLES/4
			a.datatype='long'
			a.maximum_time = maximum_time*1e6 #conversion to uS
			a.mode = EVERY_EDGE
		self.digital_channels_in_buffer = 2


	def start_four_channel_LA(self,trigger=1,maximum_time=0.001,mode=[1,1,1,1],**args):
		""" 
		Four channel Logic Analyzer.
		start logging timestamps from a 64MHz counter to record level changes on ID1,ID2,ID3,ID4.
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		trigger			Bool . Enable rising edge trigger on ID1

		maximum_time	Maximum delay expected between two logic level changes.
				If total time exceeds 1 mS, a prescaler will be used in the reference clock
				However, this only refers to the maximum time between two successive level changes. If a delay larger
				than .26 S occurs, it will be truncated by modulo .26 S.
				If you need to record large intervals, try single channel/ two channel modes which use 32 bit counters
				capable of time interval up to 67 seconds.

		mode		modes for each channel. Array with four elements
				default values: [1,1,1,1]

				EVERY_SIXTEENTH_RISING_EDGE = 5
				EVERY_FOURTH_RISING_EDGE    = 4
				EVERY_RISING_EDGE           = 3
				EVERY_FALLING_EDGE          = 2
				EVERY_EDGE                  = 1
				DISABLED		    = 0

		==============	============================================================================================

		:return: Nothing

		.. seealso::

			Use :func:`fetch_long_data_from_LA` (points to read,x) to get data acquired from channel x.
			The read data can be accessed from :class:`~Interface.dchans` [x-1]
		"""
		self.clear_buffer(0,self.MAX_SAMPLES);
		prescale = 0
		"""
		if(maximum_time > 0.26):
			#print 'too long for 4 channel. try 2/1 channels'
			prescale = 3
		elif(maximum_time > 0.0655):
			prescale = 3
		elif(maximum_time > 0.008191):
			prescale = 2
		elif(maximum_time > 0.0010239):
			prescale = 1
		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(START_FOUR_CHAN_LA)
		self.H.__sendInt__(self.MAX_SAMPLES/4)
		self.H.__sendInt__(mode[0]|(mode[1]<<4)|(mode[2]<<8)|(mode[3]<<12))
		self.H.__sendByte__(prescale) #prescaler
		trigopts=0
		trigopts |= 4 if args.get('trigger_ID1',0) else 0
		trigopts |= 8 if args.get('trigger_ID2',0) else 0
		trigopts |= 16 if args.get('trigger_ID3',0) else 0
		if (trigopts==0): trigger|=4	#select one trigger channel(ID1) if none selected
		trigopts |= 2 if args.get('edge',0)=='rising' else 0
		trigger|=trigopts
		self.H.__sendByte__(trigger)
		self.H.__get_ack__()
		self.digital_channels_in_buffer = 4
		n=0
		for a in self.dchans:
			a.prescaler = prescale
			a.length = self.MAX_SAMPLES/4
			a.datatype='int'
			a.maximum_time = maximum_time*1e6 #conversion to uS
			a.mode=mode[n]
			n+=1



	def get_LA_initial_states(self):
		""" 
		fetches the initial states before the logic analyser started

		:return: chan1 progress,chan2 progress,chan3 progress,chan4 progress,[ID1,ID2,ID3,ID4]. eg. [1,0,1,1]
		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(GET_INITIAL_DIGITAL_STATES)
		initial=self.H.__getInt__()
		A=(self.H.__getInt__()-initial)/2
		B=(self.H.__getInt__()-initial)/2-self.MAX_SAMPLES/4
		C=(self.H.__getInt__()-initial)/2-2*self.MAX_SAMPLES/4
		D=(self.H.__getInt__()-initial)/2-3*self.MAX_SAMPLES/4
		s=self.H.__getByte__()
		self.H.__get_ack__()
		
		if A==0: A=self.MAX_SAMPLES/4
		if B==0: B=self.MAX_SAMPLES/4
		if C==0: C=self.MAX_SAMPLES/4
		if D==0: D=self.MAX_SAMPLES/4
		
		if A<0: A=0
		if B<0: B=0
		if C<0: C=0
		if D<0: D=0

		return A,B,C,D,[(s&1!=0),(s&2!=0),(s&4!=0),(s&8!=0)]

		
	def fetch_int_data_from_LA(self,bytes,chan=1):
		""" 
		fetches the data stored by DMA. integer address increments

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		bytes:			number of readings(integers) to fetch
		chan:			channel number (1-4)
		==============	============================================================================================
		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(FETCH_INT_DMA_DATA)
		self.H.__sendInt__(bytes)
		self.H.__sendByte__(chan-1)
		t=np.array([self.H.__getInt__() for a in range(bytes)])
		self.H.__get_ack__()
		t=np.trim_zeros(t)
		b=1;rollovers=0
		while b<len(t):
			if(t[b]<t[b-1] and t[b]!=0):
				rollovers+=1
				t[b:]+=65535
			b+=1

		return  t

	def fetch_long_data_from_LA(self,bytes,chan=1):
		""" 
		fetches the data stored by DMA. long address increments

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		bytes:			number of readings(long integers) to fetch
		chan:			channel number (1,2)
		==============	============================================================================================
		"""
		self.H.__sendByte__(TIMING)
		self.H.__sendByte__(FETCH_LONG_DMA_DATA)
		self.H.__sendInt__(bytes)
		self.H.__sendByte__(chan-1)
		ss = self.H.fd.read(bytes*4)
		tmp = np.zeros(bytes*4)
		for a in range(bytes):
			tmp[a] = ord(ss[0+a*4])|(ord(ss[1+a*4])<<8)|(ord(ss[2+a*4])<<16)|(ord(ss[3+a*4])<<24)
		self.H.__get_ack__()
		tmp = np.trim_zeros(tmp) 
		#print '\n\n',len(ss),tmp
		return tmp


	def fetch_LA_channels(self,trigchan=1):
		"""
		reads and stores the channels in self.dchans.

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		trigchan:		channel number which should be treated as a trigger. (1,2,3,4). Its first timestamp
						is subtracted from the rest of the channels.
		==============	============================================================================================
		"""
		data=self.get_LA_initial_states()
		s=data[4]
		#print s
		for a in self.dchans:
			if a.channel_number==self.digital_channels_in_buffer: break
			samples = a.length
			if a.datatype=='int':
				tmp = self.fetch_int_data_from_LA(data[a.channel_number],a.channel_number+1)
				a.load_data(s,tmp)
			else:
				tmp = self.fetch_long_data_from_LA(data[a.channel_number*2],a.channel_number+1)
				a.load_data(s,tmp)
		
		if self.dchans[trigchan-1].dlength>1:
			#if self.dchans[trigchan-1].initial_state: offset=self.dchans[trigchan-1].timestamps[1]
			if self.digital_channels_in_buffer==1:  offset = self.dchans[trigchan-1].timestamps[0]
			else:offset=0
		else: offset = 0
		for a in self.dchans:
			if a.channel_number==self.digital_channels_in_buffer: break
			a.timestamps -= offset
			a.generate_axes()
		return True




	def get_states(self):
		"""
		gets the state of the digital inputs. returns dictionary with keys 'ID1','ID2','ID3','ID4'

		>>> print get_states()
		{'ID1': True, 'ID2': True, 'ID3': True, 'ID4': False}
		
		"""
		self.H.__sendByte__(DIN)
		self.H.__sendByte__(GET_STATES)
		s=self.H.__getByte__()
		self.H.__get_ack__()
		return {'ID1':(s&1!=0),'ID2':(s&2!=0),'ID3':(s&4!=0),'ID4':(s&8!=0)}

	def get_state(self,input_id):
		"""
		returns the logic level on the specified input (ID1,ID2,ID3, or ID4)

		+----------+-----------------------------------------------------------------+
		|Arguments |Description                                                      |
		+==========+=================================================================+
		|input_id  |  the input channel                                              |
		+          +                                                                 +
		|          |  * 'ID1' -> state of ID1                                        |
		+          +                                                                 +
		|          |  * 'ID2' -> state of ID2                                        |
		+          +                                                                 +
		|          |  * 'ID3' -> state of ID3                                        |
		+          +                                                                 +
		|          |  * 'ID4' -> state of ID4                                        |
		+----------+-----------------------------------------------------------------+

		>>> print I.get_state(I.ID1)
		False
		
		"""
		return self.get_states()[input_id]

	def set_state(self,**kwargs):
		"""
		
		set the logic level on digital outputs OD1,OD2,SQR1,SQR2

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		\*\*kwargs	OD1,OD2,SQR1,SQR2
					states(0 or 1)
		==============	============================================================================================

		>>> I.get_state(OD1=1,OD2=0,SQR1=1,SQR2=0)

		"""
		data=0
		if kwargs.has_key('OD1'):
			data|= 0x40|(kwargs.get('OD1')<<2)
		if kwargs.has_key('OD2'):
			data|= 0x80|(kwargs.get('OD2')<<3)
		if kwargs.has_key('SQR1'):
			data|= 0x10|(kwargs.get('SQR1'))
		if kwargs.has_key('SQR2'):
			data|= 0x20|(kwargs.get('SQR2')<<1)
		self.H.__sendByte__(DOUT)
		self.H.__sendByte__(SET_STATE)
		print data
		self.H.__sendByte__(data)
		self.H.__get_ack__()



	'''


	def sendBurst(self):
		"""
		Transmits the commands stored in the burstBuffer.
		empties input buffer
		empties the burstBuffer.
		
		The following example initiates the capture routine and sets OD1 HIGH immediately.
		
		It is used by the Transient response experiment where the input needs to be toggled soon
		after the oscilloscope has been started.
		
		>>> I.loadBurst=True
		>>> I.capture_traces(4,800,2)
		>>> I.set_state(OD1=1)
		>>> I.sendBurst()
		

		"""
		self.fd.write(self.burstBuffer)
		self.burstBuffer=''
		self.loadBurst=False
		acks=self.fd.read(self.inputQueueSize)
		self.inputQueueSize=0
		return [ord(a) for a in acks]
	'''

	def __get_capacitor_range__(self,ctime):
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(GET_CAP_RANGE)
		self.H.__sendInt__(ctime) 
		V_sum = self.H.__getInt__()
		self.H.__get_ack__()
		V=V_sum*3.3/16/4095
		C = -ctime*1e-6/1e4/np.log(1-V/3.3)
		return  V,C

	def get_capacitor_range(self):
		""" 
		Charges a capacitor connected to IN1 via a 20K resistor from a 3.3V source for a fixed interval
		Returns the capacitance calculated using the formula Vc = Vs(1-exp(-t/RC))
		This function allows an estimation of the parameters to be used with the :func:`get_capacitance` function.

		"""
		t=10
		P=[1.5,50e-12]
		for a in range(4):
			P=list(self.__get_capacitor_range__(20*10**a))
			if(P[0]>1.5):
				if a==0 and P[0]>3.28: #pico farads range. Values will be incorrect using this method
					P[1]=50e-12
				break
		return  P


	def get_capacitance(self,current_range,trim, Charge_Time):	#time in uS
		"""
		measures capacitance of component connected between IN1 and ground
		
		.. warning:: Non standard arguments! Needs to be rewritten

		:param int current_range: 
			current range to use (0,1,2,3) ->(550uA,.55uA,5.5uA,55uA)
		:param int trim: 
			trimming the current range selected. set as 0 
		:param int Charge_Time: 
			total time in microseconds that the current range will be activated	before measuring the voltage across it.
		:return: Voltage,Charging current used,Charging time,  Capacitance

		.. math::

			Q_{stored} = C*V
			
			I_{constant}*time = C*V
			
			C = I_{constant}*time/V_{measured}

		"""
		self.H.__sendByte__(COMMON)
		currents=[0.5775e-3,0.53e-6,0.5775e-5,0.5775e-4]
		self.H.__sendByte__(GET_CAPACITANCE)
		self.H.__sendByte__(current_range)
		if(trim<0):
			self.H.__sendByte__( int(31-abs(trim)/2)|32)
		else:
			self.H.__sendByte__(int(trim/2))
		self.H.__sendInt__(Charge_Time)
		time.sleep(Charge_Time*1e-6+.02)
		V = 3.3*self.H.__getInt__()/4095
		self.H.__get_ack__()
		Charge_Current = currents[current_range]*(100+trim)/100.0
		C = Charge_Current*Charge_Time*1e-6/V
		return V,Charge_Current,Charge_Time,C


		

	def get_inductance(self):
		"""
		measure the value of the inductor connected to the Inductance measurement unit
		
		:return: inductance
		"""
		f1=1.5491e6
		c1=1.09017e-9
		l1=9.68246e-06
		f3=self.get_high_freq('LMETER')#self.get_freq(LMETER,0.5)
		if f3>1:return (1.0/(c1*f3*f3*4*math.pi*math.pi))-l1
		else: return 0
		


	def read_flash(self,location):
		"""
		Reads 16 BYTES from the specified location

		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		location			The flash location(0 to 63) to read from .
		================	============================================================================================

		:return: a string of 16 characters read from the location
		"""
		self.H.__sendByte__(FLASH)
		self.H.__sendByte__(READ_FLASH)
		self.H.__sendByte__(location) 	#send the location
		ss=self.H.fd.read(16)
		self.H.__get_ack__()
		return ss

	def read_bulk_flash(self,bytes):
		"""
		Reads BYTES from the specified location

		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		bytes			Total bytes to read
		================	============================================================================================

		:return: a string of 16 characters read from the location
		"""
		self.H.__sendByte__(FLASH)
		self.H.__sendByte__(READ_BULK_FLASH)
		self.H.__sendInt__(bytes) 	#send the location
		ss=self.H.fd.read(bytes)
		self.H.__get_ack__()
		return ss


	def write_flash(self,location,string_to_write):
		"""
		write a 16 BYTE string to the selected location (0-63)
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		location			The flash location(0 to 63) to write to.
		string_to_write		a string of 16 characters can be written to each location
		================	============================================================================================

		"""
		while(len(string_to_write)<16):string_to_write+='.'
		self.H.__sendByte__(FLASH)
		self.H.__sendByte__(WRITE_FLASH) 	#indicate a flash write coming through
		self.H.__sendByte__(location) 	#send the location
		self.H.fd.write(string_to_write)
		time.sleep(0.1)
		self.H.__get_ack__()

	def write_bulk_flash(self,bytearray):
		"""
		write a byte array to the entire flash page. Erases any other data
		
		================	============================================================================================
		**Arguments** 
		================	============================================================================================
		bytearray		Array to dump onto flash. Max size 1024 bytes
		================	============================================================================================

		"""
		print 'Dumping ',len(bytearray),' bytes into flash'
		self.H.__sendByte__(FLASH)
		self.H.__sendByte__(WRITE_BULK_FLASH) 	#indicate a flash write coming through
		self.H.__sendInt__(len(bytearray)) 	#send the location
		for n in range(len(bytearray)):
			self.H.__sendByte__(bytearray[n])
			Printer('Bytes written: %d'%(n+1))
		time.sleep(0.2)
		self.H.__get_ack__()


	def get_ctmu_voltage(self,channel,Crange,tgen=1):
		"""
		
		:return: Voltage
		"""	
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(GET_CTMU_VOLTAGE)
		self.H.__sendByte__((channel)|(Crange<<5)|(tgen<<7))
		time.sleep(0.001)
		self.H.__getByte__()	#junk byte '0' sent since UART was in IDLE mode and needs to recover.
		#V = [self.H.__getInt__() for a in range(16)]
		#print V
		#v=sum(V)
		v=self.H.__getInt__() #16*voltage across the current source
		self.H.__get_ack__()
		V=3.3*v/15./4096
		return V


	def get_temperature(self):
		"""
		return a voltage equivalent of the on-chip temperature
		
		:return: Voltage
		"""	
		V=self.get_ctmu_voltage(0b11110,3,0)
		return (783.24-V*1000)/1.87
		


	def send_address(self,c):
		"""
		Outputs an address through the second UART
		This is used to select which PIC1572 will listen to incoming data

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		address			slave device address
		==============	============================================================================================

		:return: nothing

		"""
		self.H.__sendByte__(UART_2)
		self.H.__sendByte__(SEND_ADDRESS)
		self.H.__sendByte__(c)
		self.H.__get_ack__()


	def set_sine1(self,frequency,register=0):
		"""
		Set the frequency of sine 1
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		frequency		Frequency to set on wave generator #1 0MHz to 8MHz
		register	Frequency register to update.  The wavegen has two different registers for storing the 
				output frequency.  These are used to quickly switch between the two registers for applications
				like frequency shift keying(FSK)
		==============	============================================================================================
		
		:return: frequency
		"""
		freq_setting = int(round(1.* frequency * self.DDS_MAX_FREQ / self.DDS_CLOCK))
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_WG1)
		self.H.__sendByte__(14+register)
		self.H.__sendInt__((freq_setting)&0x3FFF)
		self.H.__sendInt__((freq_setting>>14)&0x3FFF)
		
		self.H.__get_ack__()
		return frequency

	def set_sine2(self,frequency,register=0):
		"""
		Set the frequency of sine 2
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		frequency		Frequency to set on wave generator #1 0MHz to 8MHz
		register	Frequency register to update.  The wavegen has two different registers for storing the 
				output frequency.  These are used to quickly switch between the two registers for applications
				like frequency shift keying(FSK)
		==============	============================================================================================
		
		:return: frequency
		"""
		freq_setting = int(round(1.*frequency * self.DDS_MAX_FREQ / self.DDS_CLOCK))
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_WG2)
		self.H.__sendByte__(14+register)
		self.H.__sendInt__((freq_setting)&0x3FFF)
		self.H.__sendInt__((freq_setting>>14)&0x3FFF)
		
		self.H.__get_ack__()
		return frequency

	def set_sine_phase(self,phase):
		"""
		Set the phase difference between WG1 and WG2
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		phase			Phase difference between WG1 and WG2  0-360
		==============	============================================================================================
		
		"""
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_BOTH_WG)
		self.H.__sendInt__(int(4095*phase/360.)&0x3FFF)		
		self.H.__get_ack__()

	def set_waveform_type(self,channel,waveform='sine'):
		"""
		"""
		wave={'sine':0,'triangle':1,'square':2}
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_WAVEFORM_TYPE)
		self.H.__sendByte__((1<<wave.get(waveform,0))|(0x10<<channel))		
		self.H.__get_ack__()

	def select_freq(self,channel,register):
		"""
		"""
		wave={'sine':0,'triangle':1,'square':2}
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SELECT_FREQ_REGISTER)
		self.H.__sendByte__((1<<register)|(0x10<<channel))		
		self.H.__get_ack__()


	def reload_waveform(self,channel=1,expr='sin(x)'):
		"""
		set shade of WS2182 LED on PIC1572 1 RA2
		
		.. Note:: This function normalizes and shifts the input table to the full voltage scale of the wavegen
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		Channel			Channel number. 1/2 for Sine1 or Sine2
		expr			A mathematical expression for the waveform. Supports sin,cos,tan,exp
		==============	============================================================================================
		"""
		channel=1
		x=np.linspace(0,2*np.pi,51)[:-1]
		variables={'__builtins__':None,'sin':np.sin,'cos':np.cos,'exp':np.exp,'tan':np.tan,'x':x,'X':x}
		table=eval(expr, variables)
		table=np.array(table)
		table-=min(table)	#move it into the positive domain
		table/=max(table)   #normalize
		table*=255
		self.send_address(channel)
		self.H.send_char('W')
		self.H.send_char(len(table))
		for a in table:self.H.send_char(int(round(a)))


	def set_pvs1(self,val):
		"""
		Set the voltage on PVS1
		12-bit DAC...  -5V to 5V
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		val				Output voltage on PVS1. -5V to 5V
		==============	============================================================================================

		"""
		val=int((val+5)*4095/10)
		self.write_dac(0,val)
		return val*10/4095-5

	def set_pvs2(self,val):
		"""
		Set the voltage on PVS2. Unbuffered for improved stability
		12-bit DAC...  -0 - 3.3V                                                                                                                

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		val				Output voltage on PVS2. 0-3.3V
		==============	============================================================================================
		"""
		val=int(val*4095/3.3)
		self.write_dac(1,val)
		return val*3.3/4095

	def set_pvs3(self,val):
		"""
		Set the voltage on PVS3
		5-bit DAC...  -3V to 3V

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		val				Output voltage on PVS3. -3.3V to 3.3V
		==============	============================================================================================

		:return: Actual value set on pvs3
		"""
		self.H.__sendByte__(DAC)
		self.H.__sendByte__(SET_PVS3)
		x=round((val+3.3)*31/6.6)
		self.H.__sendInt__(int(x))		#change to character!
		self.H.__get_ack__()
		return 6.6*x/31-3.3
		
	def set_pcs(self,val):
		"""
		Set programmable current source
		5-bit DAC...  0-3.3mA

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		val				Output current on PCS. 0 to 3.3mA. Subject to load resistance. Read voltage on PCS to check.
		==============	============================================================================================

		:return: value attempted to set on pcs
		"""
		self.H.__sendByte__(DAC)
		self.H.__sendByte__(SET_PCS)
		x=31-round(val*31/3.3)
		self.H.__sendInt__(int(x))		#change to character!
		self.H.__get_ack__()
		return 3.3*(32-x)/31
		
	def setOnboardLED(self,R,G,B):
		"""
		set shade of WS2182 LED on PIC1572 1 RA2
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		R				brightness of red colour 0-255
		G				brightness of green colour 0-255
		B				brightness of blue colour 0-255
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(SET_ONBOARD_RGB)
		G=reverse_bits(G);R=reverse_bits(R);B=reverse_bits(B)
		self.H.__sendByte__(B)
		self.H.__sendByte__(R)
		self.H.__sendByte__(G)
		time.sleep(0.001)
		self.H.__get_ack__()	

	def WS2182B(self,col):
		"""
		set shade of WS2182 LED on SQR1
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		col		array [R,G,B]
		R				brightness of red colour 0-255
		G				brightness of green colour 0-255
		B				brightness of blue colour 0-255
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(SET_RGB)
		R=reverse_bits(col[0]);G=reverse_bits(col[1]);B=reverse_bits(col[2])
		self.H.__sendByte__(B)
		self.H.__sendByte__(R)
		self.H.__sendByte__(G)
		self.H.__get_ack__()	

	def tune_wavegen(self,tune):
		"""
		Tune the oscillator frequency of PIC1572 (1).
		100000->111111 : no change to minimum
		000001->011111 : - to maximum
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		tune			change in clock frequency. -32 to 31
		==============	============================================================================================

		"""
		self.send_address(1)
		self.H.send_char('O')
		self.H.send_char(tune&0x3F)
		print bin(tune&0x3F)
		time.sleep(0.001)	


	def fetch_buffer(self,starting_position=0,total_points=100):
		"""
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(RETRIEVE_BUFFER)
		self.H.__sendInt__(starting_position)
		self.H.__sendInt__(total_points)
		for a in range(total_points): self.buff[a]=self.H.__getInt__()
		self.H.__get_ack__()

	def clear_buffer(self,starting_position,total_points):
		"""
		returns a section of the buffer
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(CLEAR_BUFFER)
		self.H.__sendInt__(starting_position)
		self.H.__sendInt__(total_points)
		self.H.__get_ack__()

	def start_streaming(self,tg,channel='CH1'):
		"""
		Instruct the ADC to start streaming 8-bit data.  use stop_streaming to stop.

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		tg		timegap. 250KHz clock
		channel		channel 'CH1'... 'CH9','IN1','SEN'
		==============	============================================================================================

		"""
		if(self.streaming):self.stop_streaming()
		
		self.H.__sendByte__(ADC)
		self.H.__sendByte__(START_ADC_STREAMING)
		self.H.__sendByte__(self.__calcCHOSA__(channel))
		self.H.__sendInt__(tg)		#Timegap between samples.  8MHz timer clock
		self.streaming=True

	def stop_streaming(self):
		"""
		Instruct the ADC to stop streaming data
		"""
		if(self.streaming):
			self.H.__sendByte__(STOP_STREAMING)
			self.H.fd.read(20000)
			self.H.fd.flush()
		else:
			print 'not streaming'
		self.streaming=False

	def sqr1(self,freq,duty_cycle):
		"""
		Set the frequency of sqr1

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		frequency	Frequency
		duty_cycle	Percentage of high time
		==============	============================================================================================
		"""
		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = 64e6/freq/p[prescaler]
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4:
			print 'out of range'
			return
		high_time = wavelength*duty_cycle/100.
		print wavelength,high_time,prescaler
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_SQR1)
		self.H.__sendInt__(int(round(wavelength)))
		self.H.__sendInt__(int(round(high_time)))
		self.H.__sendByte__(prescaler)
		self.H.__get_ack__()



	def sqr2(self,freq,duty_cycle):
		"""
		Set the frequency of sqr2

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		frequency	Frequency
		duty_cycle	Percentage of high time
		==============	============================================================================================
		"""
		p=[1,8,64,256]
		prescaler=0
		while prescaler<=3:
			wavelength = 64e6/freq/p[prescaler]
			if wavelength<65525: break
			prescaler+=1
		if prescaler==4:
			print 'out of range'
			return
		high_time = wavelength*duty_cycle/100.
		print wavelength,high_time,prescaler
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_SQR2)
		self.H.__sendInt__(int(round(wavelength)))
		self.H.__sendInt__(int(round(high_time)))
		self.H.__sendByte__(prescaler)
		self.H.__get_ack__()


	def set_sqrs(self,wavelength,phase,high_time1,high_time2,prescaler=1):
		"""
		Set the frequency of sqr1,sqr2, with phase shift

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		wavelength	Number of 64Mhz/prescaler clock cycles per wave
		phase		Clock cycles between rising edges of SQR1 and SQR2
		high time1	Clock cycles for which SQR1 must be HIGH
		high time2	Clock cycles for which SQR2 must be HIGH
		prescaler	0,1,2. Divides the 64Mhz clock by 8,64, or 256
		==============	============================================================================================
		
		"""
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SET_SQRS)
		self.H.__sendInt__(wavelength)
		self.H.__sendInt__(phase)
		self.H.__sendInt__(high_time1)
		self.H.__sendInt__(high_time2)
		self.H.__sendByte__(prescaler)
		self.H.__get_ack__()

	def sqr4_pulse(self,freq,h0,p1,h1,p2,h2,p3,h3):
		"""
		Output one set of phase correlated square pulses on SQR1,SQR2,OD1,OD2 .
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		freq		Frequency in Hertz
		h0		Duty Cycle for SQR1 (0-1)
		p1		Phase shift for SQR2 (0-1)
		h1		Duty Cycle for SQR2 (0-1)
		p2		Phase shift for OD1  (0-1)
		h2		Duty Cycle for OD1  (0-1)
		p3		Phase shift for OD2  (0-1)
		h3		Duty Cycle for OD2  (0-1)
		==============	============================================================================================
		
		"""
		wavelength = int(64e6/freq)
		if wavelength>65535:
			print 'frequency too low.'
			return
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SQR4)
		self.H.__sendInt__(wavelength)
		self.H.__sendInt__(int(wavelength*h0))
		params = 0
		if p1==0:p1=1
		if p2==0:p2=1
		if p3==0:p3=1
		if h1+p1>1:
			A1 = int((h1+p1)%1*wavelength)
			B1 = int((p1)*wavelength)
			params|=(1<<2)
		else:
			A1 = int(p1*wavelength)
			B1 = int((h1+p1)*wavelength)
		if h2+p2>1:
			A2 = int((h2+p2)%1*wavelength)
			B2 = int((p2)*wavelength)
			params|=(1<<3)
		else:
			A2 = int(p2*wavelength)
			B2 = int((h2+p2)*wavelength)
		if h3+p3>1:
			A3 = int((h3+p3)%1*wavelength)
			B3 = int((p3)*wavelength)
			params|=(1<<4)
		else:
			A3 = int(p3*wavelength)
			B3 = int((h3+p3)*wavelength)

		print wavelength,A1,B1,A2,B2,A3,B3
		self.H.__sendInt__(A1)
		self.H.__sendInt__(B1)
		self.H.__sendInt__(A2)
		self.H.__sendInt__(B2)
		self.H.__sendInt__(A3)
		self.H.__sendInt__(B3)
		self.H.__sendByte__(params)
		self.H.__get_ack__()

	def sqr4_continuous(self,freq,h0,p1,h1,p2,h2,p3,h3):
		"""
		Initialize continuously running phase correlated square waves on SQR1,SQR2,OD1,OD2
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		freq		Frequency in Hertz
		h0		Duty Cycle for SQR1 (0-1)
		p1		Phase shift for SQR2 (0-1)
		h1		Duty Cycle for SQR2 (0-1)
		p2		Phase shift for OD1  (0-1)
		h2		Duty Cycle for OD1  (0-1)
		p3		Phase shift for OD2  (0-1)
		h3		Duty Cycle for OD2  (0-1)
		==============	============================================================================================
		
		"""
		wavelength = int(64e6/freq)
		params=0
		if wavelength>0xFFFF00:
			print 'frequency too low.'
			return
		elif wavelength>0x3FFFC0:
			wavelength = int(64e6/freq/256)
			params=3
		elif wavelength>0x7FFF8:
			params=2
			wavelength = int(64e6/freq/64)
		elif wavelength>0xFFFF:
			params=1
			wavelength = int(64e6/freq/8)
		params|= (1<<5)
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SQR4)
		self.H.__sendInt__(wavelength)
		self.H.__sendInt__(int(wavelength*h0))

		A1 = int(p1%1*wavelength)
		B1 = int((h1+p1)%1*wavelength)
		A2 = int(p2%1*wavelength)
		B2 = int((h2+p2)%1*wavelength)
		A3 = int(p3%1*wavelength)
		B3 = int((h3+p3)%1*wavelength)

		print p1,h1,p2,h2,p3,h3
		print wavelength,int(wavelength*h0),A1,B1,A2,B2,A3,B3
		self.H.__sendInt__(A1)
		self.H.__sendInt__(B1)
		self.H.__sendInt__(A2)
		self.H.__sendInt__(B2)
		self.H.__sendInt__(A3)
		self.H.__sendInt__(B3)
		self.H.__sendByte__(params)
		self.H.__get_ack__()


	def map_reference_clock(self,scaler,*args):
		"""
		Map the internal oscillator output  to SQR1,SQR2,OD1 or OD2
		The output frequency is 128/(1<<scaler) MHz
		
		scaler [0-15]
			
			* 0 -> 128MHz
			* 1 -> 64MHz
			* 2 -> 32MHz
			* 3 -> 16MHz
			* .
			* .
			* 15 ->128./32768 MHz

		example::
		
		>>> I.map_reference_clock(2,'sqr1','sqr2')
		
		outputs 32 MHz on sqr1, sqr2 pins
		
		"""
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(MAP_REFERENCE)
		chan=0
		if 'sqr1' in args:chan|=1
		if 'sqr2' in args:chan|=2
		if 'od1' in args:chan|=4
		if 'od2' in args:chan|=8
		if 'wavegen' in args:chan|=16
		self.H.__sendByte__(chan)
		self.H.__sendByte__(scaler)
		if 'wavegen' in args: self.DDS_CLOCK = 128e6/(1<<scaler)
		self.H.__get_ack__()


	def read_program_address(self,address):
		"""
		Reads and returns the value stored at the specified address in program memory

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		address		Address to read from. Refer to PIC24EP64GP204 programming manual
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(READ_PROGRAM_ADDRESS)
		self.H.__sendInt__(address&0xFFFF)
		self.H.__sendInt__((address>>16)&0xFFFF)
		v=self.H.__getInt__()
		self.H.__get_ack__()
		return v
		
	def __write_program_address__(self,address,value):
		"""
		Writes a value to the specified address in program memory. Disabled in firmware.

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		address		Address to write to. Refer to PIC24EP64GP204 programming manual
				Do Not Screw around with this. It won't work anyway.            
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(WRITE_PROGRAM_ADDRESS)
		self.H.__sendInt__(address&0xFFFF)
		self.H.__sendInt__((address>>16)&0xFFFF)
		self.H.__sendInt__(value)
		self.H.__get_ack__()

	def read_data_address(self,address):
		"""
		Reads and returns the value stored at the specified address in RAM

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		address		Address to read from.  Refer to PIC24EP64GP204 programming manual|
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(READ_DATA_ADDRESS)
		self.H.__sendInt__(address&0xFFFF)
		v=self.H.__getInt__()
		self.H.__get_ack__()
		return v
		
	def write_data_address(self,address,value):
		"""
		Writes a value to the specified address in RAM

		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		address		Address to write to.  Refer to PIC24EP64GP204 programming manual|
		==============	============================================================================================
		"""
		self.H.__sendByte__(COMMON)
		self.H.__sendByte__(WRITE_DATA_ADDRESS)
		self.H.__sendInt__(address&0xFFFF)
		self.H.__sendInt__(value)
		self.H.__get_ack__()


	def servo(self,chan,angle):
		'''
		Output A PWM waveform on SQR1/SQR2 corresponding to the angle specified in the arguments.
		This is used to operate servo motors.  Tested with 9G SG-90 Servo motor.
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		chan			1 or 2. Whether to use SQ1 or SQ2 to output the PWM waveform used by the servo 
		angle			0-180. Angle corresponding to which the PWM waveform is generated.
		==============	============================================================================================
		'''
		if(chan==1):self.set_sqr1(10000,750+int(angle*1900/180),2)
		elif(chan==2):self.set_sqr2(10000,750+int(angle*1900/180),2)

	def servo4(self,a1,a2,a3,a4):
		"""
		Operate Four servo motors independently using SQR1, SQR2, OD1, OD2.
		tested with SG-90 9G servos.
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		a1			Angle to set on Servo which uses SQR1 as PWM input. [0-180]
		a2			Angle to set on Servo which uses SQR2 as PWM input. [0-180]
		a3			Angle to set on Servo which uses OD1 as PWM input. [0-180]
		a4			Angle to set on Servo which uses OD2 as PWM input. [0-180]
		==============	============================================================================================
		
		"""
		params = (1<<5)|2		#continuous waveform.  prescaler 2( 1:64)
		self.H.__sendByte__(WAVEGEN)
		self.H.__sendByte__(SQR4)
		self.H.__sendInt__(10000)		#10mS wavelength
		self.H.__sendInt__(750+int(a1*1900/180))
		self.H.__sendInt__(0)
		self.H.__sendInt__(750+int(a2*1900/180))
		self.H.__sendInt__(0)
		self.H.__sendInt__(750+int(a3*1900/180))
		self.H.__sendInt__(0)
		self.H.__sendInt__(750+int(a4*1900/180))
		self.H.__sendByte__(params)
		self.H.__get_ack__()


	def enableUartPassthrough(self,baudrate):
		'''
		All data received by the device is relayed to an external port(SCL[TX],SDA[RX]) after this function is called
		
		If a period > .5 seconds elapses between two transmit/receive events, the device resets
		and resumes normal mode. This timeout feature has been implemented in lieu of a hard reset option.
		can be used to load programs into secondary microcontrollers with bootloaders such ATMEGA, and ESP8266
		
		
		==============	============================================================================================
		**Arguments** 
		==============	============================================================================================
		baudrate	BAUD9600... BAUD1000000
		==============	============================================================================================
		'''
		self.H.__sendByte__(PASSTHROUGHS)
		self.H.__sendByte__(PASS_UART)
		self.H.__sendByte__(baudrate)
		print 'junk bytes read:',len(self.H.fd.read(100))



	def estimateDistance(self):
		'''
		Read data from ultrasonic distance sensor HC-SR04/HC-SR05.  Sensors must have separate trigger and output pins.
		First a 10uS pulse is output on OD1.  Therefore OD1 must be connected to the TRIG pin on the sensor prior to use.

		The sensor then outputs an electrical pulse whose width is equal to the time taken by the sound pulse to return to
		the source.
		Therefore its output pin must be connected to ID1 prior to usage.


		The ultrasound sensor outputs a series of 8 sound pulses at 40KHz which corresponds to a time period
		of 25uS per pulse. These pulses reflect off of the nearest object in front of the sensor, and return to it.
		The time between sending and receiving of the pulse packet is used to estimate the distance.
		If the reflecting object is either too far away or absorbs sound, less than 8 pulses may be received, and this
		can cause a measurement error of 25uS which corresponds to 8mm.
		
		'''
		self.H.__sendByte__(NONSTANDARD_IO)
		self.H.__sendByte__(HCSR04_HEADER)

		timeout_msb = int((0.1*64e6))>>16
		self.H.__sendInt__(timeout_msb)

		A=self.H.__getLong__()
		B=self.H.__getLong__()
		tmt = self.H.__getInt__()
		self.H.__get_ack__()
		#print A,B
		if(tmt >= timeout_msb or B==0):return 0
		rtime = lambda t: t/64e6
		return rtime(B-A+20)





if __name__ == "__main__":
	print """this is not an executable file
	from Labtools import interface
	I=interface.Interface()
	
	You're good to go.
	
	eg.
	
	I.get_average_voltage('CH1')
	"""
