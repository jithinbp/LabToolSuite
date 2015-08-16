'''
This App uses data acquired from an MPU6050 accelerometer module and uses it to position the mouse cursor

'''
if __name__ == "__main__":
	import pymouse
	P=pymouse.PyMouse()

	import numpy as np
	from Labtools import interface


	I=interface.Interface()
	from gyro import *
	gyro=MPU6050(I)

	noise1=[];noise2=[]
	for a in range(500):
		x,y,z=gyro.getAccel()
		noise1.append(np.arcsinh(x*np.pi))
		noise2.append(np.arcsinh(y*np.pi))
	std1 = np.std(noise1);std2 = np.std(noise2)
	var1 = 1e-4;var2=1e-4

	eVar1 = std1 ** 2  # 0.05 ** 2
	eVar2 = std2 ** 2  # 0.05 ** 2
	K1 = KalmanFilter(var1, eVar1)
	K2 = KalmanFilter(var2, eVar2)

	while 1:
		x,y,z = gyro.getAccel()
		K1.input_latest_noisy_measurement(np.arcsinh(x*np.pi))
		K2.input_latest_noisy_measurement(np.arcsinh(y*np.pi))
		V1=K1.get_latest_estimated_measurement()
		V2=K2.get_latest_estimated_measurement()
		P.move((V2+0.5)*4*400,(V1+0.5)*4*200)
