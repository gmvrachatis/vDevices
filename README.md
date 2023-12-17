**_vDevices_**

These simulated devices faithfully replicate the behavior and operations of their physical counterparts, enabling accurate testing and validation of IoT applications and protocols. Leveraging GNS3's scalable architecture, these virtual devices offer a dynamic platform for network engineers, researchers and enthusiasts to experiment and innovate in a controlled environment. The provided virtual ecosystem enables users to explore IoT scenarios, from temperature regulation to surveillance, enabling integrated testing and development in the evolving landscape of the Internet of Things.

<br><br><br><br><br>
**Using the Paho library and Docker technology, the following IoT devices are created:**

- **vHeater** is a device that is designed to simulate the operation of a heater

- **vCooler** is a device designed to simulate the operation of a cooler.

- **vThermostat** is a device designed to simulate the operation of a thermostat. 

- **vFridge** is a device designed to simulate the operation of a smart fridge.

- **vCamera** is a device that is designed to simulate the operation of a smart camera

- **vSwitch** is a device that is designed to simulate the operation of a smart switch.

- **vController** is a device that is designed to simulate the operation of a recorder and/or a power management unit.

<br><br>
vDevice architecture and features:
1.	The vDevices are available on dockerhub for use with GNS3 (gmvra/vcamera, gmvra/vcontroller and more) and the code is on github
2.	The vDevices use the newest version of Alpine Linux.
3.	Some arguments may be required while initializing the vDevices
4.	They have the ability to save their state and at any time and it is needed to stop their operation and they can resume where they left off.
5.	It is possible to change device variables with python commands.
6.	In order to maintain simplicity and conserve resources consumed by each device, no security measures are used
