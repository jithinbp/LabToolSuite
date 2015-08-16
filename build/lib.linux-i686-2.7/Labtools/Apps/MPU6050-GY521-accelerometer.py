import Labtools.interface as interface
from Labtools.experiment import *
import numpy as np
from Labtools.MPU6050 import *
import pyqtgraph as pg


if __name__ == "__main__":
	I=interface.Interface()
	Exp=Experiment(parent=None,graph3D=True,showresult=False,I=I)
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

	gyro=MPU6050(I)


	noise1=[]
	noise2=[]
	noise3=[]
	for a in range(500):
		vals=gyro.getAccel()
		color=(gyro.getTemp()-.937)*100
		S1=vals[0]
		S2=vals[1]
		noise1.append(np.arcsinh(S1*np.pi))
		noise2.append(np.arcsinh(S2*np.pi))
		noise3.append(color)
	std1 = np.std(noise1)
	std2 = np.std(noise2)
	std3 = np.std(noise3)
	var1 = .8e-1
	var2=.8e-1
	var3=.8e-4
	eVar1 = std1 ** 2  # 0.05 ** 2
	eVar2 = std2 ** 2  # 0.05 ** 2
	eVar3 = std3 ** 2  # 0.05 ** 2
	K1 = KalmanFilter(var1, eVar1)
	K2 = KalmanFilter(var2, eVar2)
	K3 = KalmanFilter(var3, eVar3)

	#tmp=ComplementaryFilter()

	def setAngle():
		color=(gyro.getTemp()-.937)*100
		vals=gyro.getAccel()
		S1=vals[0]
		S2=vals[1]
		K1.input_latest_noisy_measurement(np.arcsinh(S1*np.pi))
		K2.input_latest_noisy_measurement(np.arcsinh(S2*np.pi))
		K3.input_latest_noisy_measurement(color)
		#vals=gyro.getRaw()
		#tmp.addData([(vals[0]*360+180)%360,(vals[1]*360+180)%360,(vals[2]*360+180)%360],[vals[4],vals[5]])
		V1=K1.get_latest_estimated_measurement()
		V2=K2.get_latest_estimated_measurement()
		color=K3.get_latest_estimated_measurement()
		surf.shader()['colorMap'] = np.array([color, color*2,1.])
		
		plot.setCameraPosition(elevation=V1*90,azimuth = V2*90)

	Exp.loopTask(1,setAngle)
	Exp.run()
