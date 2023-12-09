vController is a device which is designed to simulate the operation of a logger or (and/or) a power management unit.

In the case of the recorder, the device registers in the threads "cameras/#/#/trigered", "cameras/outside/#/trigered", "cameras/#/#/feed" and "cameras/outside/#/feed" and simply receives the messages. While in the other case it registers in the "power/used" topic and calculates at specified intervals (by or from the user) the power consumption.(Dockerhub: gmvra/vcontroller

**How to Start :**

As all vDevices, vCamera is configured by arguments

The following arguments are:
		

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/ed597ebb-5b1a-40e8-8ce9-c0f81c8dc4b4)


(Example) <code> python vThermostat -b broker.emqx.io -r Bedroom1 -n b1Thermostat </code>


It can be changed while it is running by changing the following variables with python commands

**The variables are:**

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/11db8a30-699b-4fdf-9071-02c9d5151b7b)


**TOPICS :**

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/2b929805-830d-4b87-a774-b7e20cf84b38)

