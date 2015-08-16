'''calibrate all four bipolar inputs using PVS1*2 (-6.6-6.6V)
Connect all inputs to PVS1x2 before starting

Author:Jithin

'''
import numpy as np
import serial,time,string,sys
import struct

class Printer():
    """
    Print things to stdout on one line dynamically
    """
 
    def __init__(self,data):
 
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()

import interface

I=interface.Interface()
f=open('calib_data/calibs.py','wt')
f.write('calibs={')
CALFACS=[]

def addEntry(name,vals,comma=False):
	global f,CALFACS
	f.write("\n'%s':["%(name))
	n=0
	for val in vals:
		f.write("[%.4e,%.4e,%.4e], #gain: %dx\n"%(val[0],val[1],val[2],I.gain_values[n]) )
		CALFACS+=[ord(a) for a in struct.pack('3f',*val)]
		n+=1
	f.write(']')
	if comma: f.write(',')

def getv(chan):
	return I.__get_raw_average_voltage__(chan)

channel_names=['CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','CH9']
CALDATA={}
fits={}
for val in channel_names:
	fits[val]=[]

for gain in range(8):
	for x in channel_names:
		I.set_gain(x,gain)
		CALDATA[x]=[]
	time.sleep(0.02)
	DAC = np.linspace(0.6/I.gain_values[gain],3.0/I.gain_values[gain],200)
	for val in DAC:
		I.set_pvs2(val)
		for n in channel_names:
			CALDATA[n].append(getv(n))

	DAC = (np.int0(DAC*4095/3.3))*3.3/4095
	Printer('Calibrating Amplifiers -----------> %dx'%(I.gain_values[gain]))
	for val in channel_names:
		fits[val].append(np.polyfit(CALDATA[val],DAC,2))

Printer('Calibrating Amplifiers : %dx --------> DONE \n'%(I.gain_values[7]))


for val in channel_names:
	addEntry(val,fits[val],True)

ft=np.poly1d(fits['CH1'][0])
print 'testing',ft(0),ft(1023)

f.write('}\n')

I.write_bulk_flash(CALFACS)
'''
CH1str = struct.pack('3f',*fits['CH1'])
CH2str = struct.pack('3f',*fits['CH2'])
CH3str = struct.pack('3f',*fits['CH3'])
CH4str = struct.pack('3f',*fits['CH4'])

print CH1str
print CH2str
print CH3str
print CH4str

print struct.unpack('3f',CH1str)
print struct.unpack('3f',CH2str)
print struct.unpack('3f',CH3str)
print struct.unpack('3f',CH4str)
'''

