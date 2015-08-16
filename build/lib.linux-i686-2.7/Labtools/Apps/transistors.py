#!/usr/binpython
'''
Characterise PNP, NPN transistors using the programmable current source and voltage sources



'''
from Labtools import interface
from Labtools.experiment import *
from Labtools.templates.template_trans import Ui_Form


class Handler(QFrame,ConvenienceClass,Ui_Form):
	def __init__(self,exp):
		super(Handler, self).__init__()
		self.Exp=exp
		self.setupUi(self)
		self.I = interface.Interface()
		self.splitter.setSizes([1,0])
		self.base_current=0
		self.base_voltage=0
		self.seriesR=1000.
		self.timegap=0
		self.MAXV=2.0
		self.MINV=0.0
		self.transistor_type='NPN'
		self.looptimer=QTimer()
		self.X=[]
		self.Y=[]
		self.curves=[]
		self.legends=[]
		self.curveData={}
		self.plot = Exp.add2DPlot()
		
		self.plot.setLabel('bottom', 'Voltage -->>', units='V')
		self.plot.setLabel('left', 'Current -->>', units='A')
		self.plot.showGrid(True,True)
		self.newcol=self.random_color()
		self.current_curve=Exp.addCurve(self.plot,self.IbeLabel.text(),self.newcol)
		self.setBaseCurrent(0)
		self.I.set_pvs1(0)
		self.Exp.setRange(self.plot,-5,-20e-3,10,40e-3)

	def start(self,x=None):
		self.X=[];self.Y=[]
		self.Vval=self.MINV
		if(not self.looptimer.isActive()):self.looptimer=self.loopTask(self.timegap,self.acquire,0)


	def setBaseCurrent(self,i):
		i=self.I.set_pcs(3.3*i/4095)
		self.base_current = i
		self.IbeLabel.setText('I_be = %0.3f mA'%(i))

	def setBaseVoltage(self,i):
		i=self.I.set_pvs3(6.6*i/4095-3.3)
		self.base_voltage = i
		self.updateBaseCurrent()

	def setSeriesR(self,i):
		self.seriesR=i
		self.updateBaseCurrent()

	def updateBaseCurrent(self):
		self.base_current = 1.e3*self.base_voltage/self.seriesR
		self.IbeLabel2.setText('I_be = %0.3f mA'%(self.base_current))
		

	def delete_curve(self):
		c = self.saved_traces.currentIndex()
		if c>-1:
			self.saved_traces.removeItem(c)
			#self.curveData.pop(c)
			self.plot.removeItem(self.curves[c]);	self.plot.removeItem(self.legends[c])
			self.curves.pop(c);	self.legends.pop(c)
			
	def changeTransistorType(self,t):		
		if(t):
			self.transistor_type='PNP'
			#self.PNP_Frame.setEnabled(True);self.NPN_Frame.setEnabled(False);
			self.splitter.setSizes([0,1])
			self.MINV=-2.0;self.MAXV=0.
		else:
			self.transistor_type='NPN'
			#self.NPN_Frame.setEnabled(True);self.PNP_Frame.setEnabled(False);
			self.splitter.setSizes([1,0])
			self.MINV=0.;self.MAXV=2.
		self.Exp.set2DRange(self.MINV-1,-20e-3,(self.MAXV-self.MINV+2)*1.2,40e-3)

	def saveData(self):
		filename = self.filename_text.text()
		if not len(self.curveData):
			print 'No data yet'
			return
		f=open(filename,'wt')
		for a in self.curveData:
			x,y=self.curveData[a]
			for num in range(len(x)):
				f.write('%0.4e %0.4e\n'%(x[num],y[num]))
			f.write('\n')
		f.close()				
		print 'saved to :',filename

	def acquire(self,chan):
		self.I.set_pvs1(self.Vval)
		V=self.Vval
		I=self.I.get_average_voltage('CH1')/441
		self.VceLabel.setText('V_ce = %0.2fV'%(V));	self.IceLabel.setText('I_ce = %0.2fmA'%(I*1e3))
		self.X.append(V);self.Y.append(I)
		self.progress.setValue(round((self.Vval-self.MINV)*100/(self.MAXV-self.MINV)))
		self.Vval+=0.01
		self.current_curve.setData(self.X,self.Y)
		if(self.Vval>self.MAXV):
			self.looptimer.stop()
			self.I.set_pvs3(0);self.I.set_pcs(0);
			self.curves.append(self.current_curve)
			lbl='I_be = %0.2fmA'%(self.base_current)
			self.curveData[lbl]=[self.X,self.Y]
			self.saved_traces.addItem(lbl)
			self.saved_traces.setItemData(self.saved_traces.count()-1, QColor(*self.newcol), Qt.BackgroundRole);
			self.saved_traces.setItemData(self.saved_traces.count()-1, QColor(255,255,255), Qt.ForegroundRole);
			self.newcol=self.random_color()
			self.current_curve=self.Exp.addCurve(self.plot,self.IbeLabel.text(),self.newcol)
			txt='<div style="text-align: center"><span style="color: #FFF;font-size:8pt;">'+lbl+'</span></div>'
			if self.transistor_type=='NPN':anchor=(0,0)
			else:anchor=(1,0)
			text = pg.TextItem(html=txt, anchor=anchor, border='w', fill=(0, 0, 255, 100))
			self.plot.addItem(text)
			self.legends.append(text)
			if self.transistor_type=='NPN':text.setPos(self.X[-1],self.Y[-1])
			else:
				text.setPos(self.X[0],self.Y[0])

	def showData(self):
		tmpdata={}
		for a in self.curveData:
			tmpdata[a]=np.column_stack(self.curveData[a])
		self.displayObjectContents(tmpdata)

if __name__ == "__main__":
	Exp=Experiment(parent=None,graph2D=True,showresult=True)
	handler = Handler(Exp)
	Exp.addHandler(handler)
	Exp.run()
