import Labtools.interface as interface
from Labtools.experiment import *
from Labtools.templates.template_bandpass import Ui_Form
#from agilent import *

import numpy as np
import scipy.optimize as optimize
import scipy.fftpack as fftpack


class Handler(QFrame,ConvenienceClass,Ui_Form):
	def __init__(self):
		super(Handler, self).__init__()
		self.setupUi(self)
		self.I = interface.Interface()
		#self.funcgen= agilent('192.168.1.3')
		self.I.configure_trigger(0,0)
		self.looptimer=QTimer()
		self.plot1 = Exp.add2DPlot()
		self.plot2 = Exp.add2DPlot()
		self.curve1 = Exp.addCurve(self.plot1,'INPUT',(255,255,255))
		self.curve2 = Exp.addCurve(self.plot1,'OUTPUT',(0,255,255))

		self.p2=Exp.enableRightAxis(self.plot2)
		self.plot2.getAxis('right').setLabel('Phase', color='#00ffff')
		self.plot2.getAxis('left').setLabel('Amplitude', color='#ffffff')
		for a in [self.plot1,self.plot2]:a.getAxis('bottom').setLabel('Frequency', color='#ffffff')
		self.p2.setYRange(-360,360)

		self.curvePhase=Exp.addCurve(self.p2)#pg.PlotCurveItem()
		#self.p2.addItem(self.curvePhase)
		self.curvePhase.setPen(color=(0,255,255), width=1)
		self.curveAmp = self.plot2.plot()
		self.curveAmp.setPen(color=(255,255,255), width=1)
		self.freqs=[]
		self.amps=[]
		self.dP=[]
		self.STARTFRQ=self.startFreq.value()		
		self.ENDFRQ=self.stopFreq.value()
		self.frq=self.STARTFRQ
		self.STEPFRQ=self.stepFreq.value()
		self.loop=None
		self.plot2.setXRange(self.STARTFRQ,self.ENDFRQ)
		self.plot2.setYRange(0,1.)
		self.active=False


	def setStartFreq(self,val):
		self.STARTFRQ=val		
	def setStopFreq(self,val):
		self.ENDFRQ=val		
	def setFreqStep(self,val):
		self.STEPFRQ=val		

	def startSweep(self):
		if(self.active):
			return
		self.STARTFRQ=self.startFreq.value()		
		self.ENDFRQ=self.stopFreq.value()
		self.active=True
		self.I.set_sine1(self.frq)
		time.sleep(1)
		self.loop = Exp.delayedTask(100,self.newset)

	def stopSweep(self):
		self.active=False
		
	def newset(self):
		if(not self.active):return
		frq = self.I.set_sine1(self.frq)
		#self.funcgen.go("FREQ "+str(val))
		time.sleep(0.1)

		tg=int(1e6/frq/1000)+1
		self.I.capture_traces(2,1800,tg)
		self.loop=Exp.delayedTask(3200*tg*1e-3+50,self.plotData,frq)
		
		self.frq+=self.STEPFRQ
		if(self.ENDFRQ>self.STARTFRQ):self.progress.setValue(100*(1.*(self.frq-self.STARTFRQ)/(self.ENDFRQ-self.STARTFRQ)))
		if(self.frq>self.ENDFRQ):
			self.active=False

	def plotData(self,frq):		
		if(not self.active):return
		x,y=self.I.fetch_trace(1)
		self.curve1.setData(x,y)
		a1,f1,p1,o1,chisq1 = self.fitData(x,y)
		
		x,y=self.I.fetch_trace(2)
		#y=y/4.		#REMOVE WHEN USED WITH PROTO 4
		self.curve2.setData(x,y)
		a2,f2,p2,o2,chisq2 = self.fitData(x,y,frequency=f1)
		
		if a2 and a1:
			self.msg.setText("Set F:%.1f\tFitted F:%.1f"%(frq,f1))
			self.freqs.append(f1)
			self.amps.append(a2/a1)
			p2=(p2)
			p1=(p1)
			dp=(p2-p1)-360
			if dp<-360:dp+=360
			self.dP.append(dp)
		else:
			print 'err!',
		print '%d:\tF: %.2f,%.2f\tA: %.2f,%.2f\tP: %.1f,%.1f'%(frq,f1,f2,a1,a2,p1,p2)
		#print chisq2[0]
		self.curveAmp.setData(self.freqs,self.amps)
		self.curvePhase.setData(self.freqs,self.dP)
		self.loop=Exp.delayedTask(10,self.newset)
		
		

	def showData(self):
		self.displayObjectContents({'Frequency Response':np.column_stack([self.freqs,self.amps,self.dP])})

	def clearData(self):
		self.freqs=[]
		self.amps=[]
		self.dP=[]
		self.curveAmp.clear()
		self.curvePhase.clear()
		self.frq=self.STARTFRQ
		print 'cleared data'

if __name__ == "__main__":
	Exp=Experiment(parent=None,showresult=False)
	handler = Handler()
	handler.I.set_gain('CH1',2)	#CHANGE GAIN CHANNEL TO 1 
	handler.I.set_gain('CH2',2)	#CHANGE GAIN CHANNEL TO 2 
	Exp.addHandler(handler)
	Exp.run()
