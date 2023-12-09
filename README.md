vCamera is a device which is designed to simulate the operation of a smart camera. 

It has the ability to operate in two different modes at any quality (resolution and framerate). The first mode is called real-time and has the ability to send the feed that the camera is "seeing" at that moment. While on the other hand there is the detection mode where with the help of the OpenCV2 library it has the ability to detect various changes in the videos and send the snapshots. A video is loaded on the device during which it randomly switches from white to black and repeats itself so that the device can operate without any actual camera working.

How to Start :

As all vDevices, vCamera is configured by arguments

The following arguments are:

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/e2eb63a9-e526-4d37-a0b1-24e1455dccbe)

(Example) <code> python vThermostat -b broker.emqx.io -n camera1


It can be changed while it is running by changing the following variables with python commands

**The variables are:**

![image](https://github.com/gmvrachatis/vDevices/assets/66122405/92934403-372e-4969-b5f0-f0cd915dba9d)

**TOPICS :**


![image](https://github.com/gmvrachatis/vDevices/assets/66122405/659c09b7-5b45-4926-87b0-261b41907e5d)







