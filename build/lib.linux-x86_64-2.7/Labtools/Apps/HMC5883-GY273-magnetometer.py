import Labtools.interface as interface
from Labtools.experiment import *
import numpy as np
from Labtools.HMC5883L import *
import pyqtgraph as pg


if __name__ == "__main__":
	Exp=Experiment(parent=None,graph3D=True,showresult=False)
	plot = Exp.add3DPlot()
	surf = Exp.new3dSurface(plot,shader='heightColor',smooth=False,computeNormals=True)
	color=.9
	surf.shader()['colorMap'] = np.array([color, color+.1,0.4, 0.5, 0.7, color-.2, 0.9,1.0])
	surf.scale(20./50,20./500,20./16.5)
	surf.translate(-10,-10,0)

	surfdata=[]
	for x in range(50):
		surfdata.append(np.sin(np.linspace(0,5*np.pi,500)))
	Exp.setSurfaceData(surf,surfdata)
	I=interface.Interface()

	mag=HMC5883L()
	mag.connect()

	def setAngle():
		vals=mag.read()
		mod = np.sqrt(vals[0]**2+vals[1]**2+vals[2]**2)
		V1 = (vals[0]/mod)
		V2 = (vals[1]/mod)
		plot.setCameraPosition([0,0,0],30,V1*90,V2*90)

	Exp.loopTask(1,setAngle)
	Exp.run()
