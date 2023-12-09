vFridge is a device which is designed to simulate the operation of a smart refrigerator. Using the library it has the ability to simulate a multi-zone refrigerator. Using the same thermodynamic function as vThermostat and seeing the number of zones that wish to reduce its temperature it can separate the total thermal energy of the appliance and simulate the temperature reduction of each zone separately. 


As all vDevices, vCamera is configured by arguments

The following arguments are:

					
![image](https://github.com/gmvrachatis/vDevices/assets/66122405/cb91e751-5d1e-4f7f-abc7-f2713078b7d2)


(Example) <code> python vThermostat -b broker.emqx.io -r kitchen1 -n fridge1 -z 4 </code>


It can be changed while it is running by changing the following variables with python commands

**The variables are:**

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/d495a45d-1a16-4c35-95c6-887f3b4a3c1b)

**TOPICS :**

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/4adcfe19-7263-4547-b213-ea996b1ab303)

