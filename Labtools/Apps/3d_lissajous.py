from Labtools.experiment import *
import Labtools.interface as interface
from Labtools.templates.template_liss import Ui_Form


class Handler(QFrame,ConvenienceClass,Ui_Form):
	def __init__(self,exp=None):
		super(Handler, self).__init__()
		self.Exp=exp
		self.setupUi(self)
		self.I = interface.Interface()
		self.delay=100
		self.plot = self.Exp.add3DPlot()
		self.looptimer=QTimer()
		self.Xchan=1
		self.Ychan=2
		self.Zchan=3
		self.samples=800
		self.scaleX=20/16.5;self.offX=0
		self.scaleY=20/16.5;self.offY=0
		self.scaleZ=20/16.5;self.offZ=0
		self.setSine1(100)
		self.setSine2(100)
		self.tg=1
		self.launchacquire=self.delayedTask(self.delay,self.acquire)

	def setSine1(self,f):
		f=self.I.set_sine1(f)
		self.sine1Label.setText('sine1=%.1fHz'%(f))
	def setSine2(self,f):
		f=self.I.set_sine2(f)
		self.sine2Label.setText('sine2=%.1fHz'%(f))

	def setXchan(self,v):
		self.Xchan=v+1
	def setYchan(self,v):
		self.Ychan=v+1
	def setZchan(self,v):
		self.Zchan=v+1

	def setTimegap(self,tg):
		self.tg=tg
		self.tgLabel.setText('dT =%duS'%(tg))

	def acquire(self):
		self.I.capture_traces(4,self.samples,self.tg)
		self.launchdisplay=self.delayedTask(self.tg*self.samples*1e-6+10,self.display)
		
	def display(self):
		X=self.I.fetch_trace(self.Xchan)[1]		#returns t,y.  We just need Y
		Y=self.I.fetch_trace(self.Ychan)[1]
		Z=self.I.fetch_trace(self.Zchan)[1]
		self.Exp.clearLinesOnPlane(self.plot)
		self.Exp.draw3dLine(self.plot,np.array(Z)*self.scaleZ+self.offZ,np.array(X)*self.scaleX+self.offX,np.array(Y)*self.scaleY+self.offY,(0,100,255))
		self.launchacquire=self.delayedTask(self.delay,self.acquire)

if __name__ == "__main__":
	Exp=Experiment(parent=None,showresult=False)
	handler = Handler(Exp)
	Exp.addHandler(handler)
	Exp.run()
