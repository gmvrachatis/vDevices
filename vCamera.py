import argparse
import imutils
import cv2
import paho.mqtt.client as mqtt_client
import datetime
import hashlib
import random
import continuous_threading
import time


flag_auto="OFF"
flag_realtime="OFF"
video=None
sleep=60


def get_uid():
	current_datetime = datetime.datetime.now()
	datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
	datetime_string= datetime_string + str(random.randint(-10000,10000))

	sha2_hash = hashlib.sha512()
	sha2_hash.update(datetime_string.encode())
	hash_result = sha2_hash.hexdigest()

	return hash_result



#STORE IT ON FILE AND TRACEBACK WHAT IN FOLDER
filename = 'uid.txt'
try:
    file = open(filename, 'a+')  # Open the file in append mode (read and write)
    file.seek(0)  # Move the file pointer to the beginning
    content = file.read()  # Read the file content
      
    if content:
        uid=content

    else:
        print("File created successfully.")
        uid=get_uid()	
        file.write(uid)
        # Perform any necessary operations if the file was just created
    file.close()# Close the file when done

except IOError:
    print("An error occurred while opening or creating the file.")
    exit()







#create data storing file and reading from it
filename = 'data.txt'
variables = ['broker','camera-name','port','room','power','idle-power','first-time','framerate','resolution-width','resolution-height','video','min-area'] 


try:
    file = open(filename, 'a+')
    file.seek(0)
    content = file.read()
    file.close()

    if content:
        data = eval(content)  # Convert the content string to a dictionary
        data['first_time']=False
    else:
        print("File created successfully.")
        data = {}  # Create an empty dictionary to store the variables

        # Get input for each variable and store in the dictionary
        for variable in variables:
            data[variable] = None
            if variable=="port":
                data["port"]=1883
            elif variable=='first-time':
                data['first-time']=True

        file = open(filename, 'w')  # Reopen the file in write mode
        file.write(str(data))  # Write the dictionary as a string to the file
        file.close()

    # Access the variables
    
    broker = str(data['broker'])
    port = int(data['port'])
    room = str(data['room'])
    camera_name = str(data['camera-name'])
    
    video = str(data['video'])
    
    framerate = str(data['framerate'])
    try:
        min_area = int(data['min-area'])
    except:
        min_area = 500
    try:
        resolution_height=int(data['resolution-height'])
        resolution_width=int(data['resolution-width'])
        framerate=int(data['framerate'])
    except:
        resolution_height=1080
        resolution_width=1920
        framerate=60

    try:
        idle_power = int(data['idle-power'])
    except:
        idle_power=0  
    try:
        power = int(data['power'])
    except:
        power=0
    first_time=data['first-time']


except IOError:
    print("An error occurred while opening or creating the file.")
    exit()





#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time==True:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-n", "--name",required=True, type=str,help="Unique name for the camera")
    ap.add_argument("-p", "--port",type=int,help="Broker listening port")
    ap.add_argument("-v", "--video",type=str,default="video.mp4",help="Path Video that gets looped")
    ap.add_argument("-r", "--room",type=str,default=None, help="id of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=3, help="Add power in W/s while running")
    ap.add_argument("-a", "--min-area", type=int,default=500, help="minimum area size for movement detection")
    ap.add_argument("-iP", "--idle-power", type=int,default=0, help="Add power in W/s while idle")
    ap.add_argument("-f", "--framerate", type=int,default=60, help="Framerate that the camera records")
    ap.add_argument("-x", "--resolution-width", type=int,default=1920, help="Resolution of the camera resolutionwidth")
    ap.add_argument("-y", "--resolution-height", type=int,default=1080, help="Resolution of the camera resolution height")
else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-n", "--name",type=str,help="Unique name for the camera")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-v", "--video",type=str,default=video,help="Video that gets looped")
    ap.add_argument("-r", "--room",type=str,default=room , help="id of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=power, help="Add power in W/s while running")
    ap.add_argument("-a", "--min-area", type=int,default=min_area, help="minimum area size for movement detection")
    ap.add_argument("-iP", "--idle-power", type=int,default=idle_power, help="Add power in W/s while idle")
    ap.add_argument("-f", "--framerate", type=int,default=framerate, help="Framerate that the camera records")
    ap.add_argument("-x", "--resolution-width", type=int,default=resolution_width, help="Resolution of the camera width")
    ap.add_argument("-y", "--resolution-height", type=int,default=1080, help="Resolution of the camera height")



args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["name"]!=None:
    camera_name = args["name"]

if args["port"]!=None :
    port = args["port"]

if args["room"]!=None:
    room=args["room"]

if args["video"]!=None:
    video=args["video"]

try:
        resolution_height = int(args["resolution-height"])
except:
        resolution_height=resolution_height 

try:
        min_area = int(args["min-area"])
except:
        min_area=min_area 

try:
        resolution_width = int(args["resolution-width"])
except:
        resolution_width=resolution_width

try:
        idle_power = int(args["idle-power"])
except:
        idle_power=idle_power 
try:
        power = int(args["power"])
except:
        power=power
    



def save():
    #Recall changed data
    filename='data.txt'
    variables = ['broker','camera-name','port','room','power','idle-power','first-time','framerate','resolution-width','resolution-height','video','min-area'] 
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,camera_name,port,room,power,idle_power,first_time,framerate,resolution_width,resolution_height,video,min_area] 
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()


save()



topics={    "topic_alarm_all_minus_outside":"cameras/outside/flag" if room==None else None,
            "topic_alarm_all":"cameras/+/flag",
            "topic_alarm_room":"cameras/room"+room+"/+/flag" if not room==None else None,
            "topic_camera_feed":"cameras/"+ room +"/"+ camera_name+"/trigered" if not room==None else "cameras/outside/"+ camera_name+"/trigered",
            "topic_camera_realtime_feed":"cameras/"+ room +"/"+ camera_name+"/feed" if not room==None else "cameras/outside/"+ camera_name +"/feed",
            "topic_camera_realtime_feed_flag":"cameras/"+ room+"/"+ camera_name+"/feed" if not room==None else "cameras/outside/"+ camera_name+"/feed"
        }


def vCamera(client):
    global flag_auto, flag_realtime, framerate, resolution_height, resolution_width, video, min_area
    # loop over the frames of the video, and store corresponding information from each frame
    vs = cv2.VideoCapture(video)
    firstFrame = None
    frame_delay = 1 / framerate
    frame = None
    # repeating and finding movement
    while True:
        start_time = time.time()
        ret, frame = vs.read()

        # If the frame can not be grabbed, then restart the video
        if not ret:
            vs.release()
            vs = cv2.VideoCapture(video)
            continue

        if flag_realtime == True:
            _, frame_to_jpg=cv2.imencode('.jpg', frame)
            frame_bytes = frame_to_jpg.tobytes()
            client.publish(topics["topic_camera_realtime_feed"], frame_bytes)

        if flag_auto == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # If the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            # Compute the absolute difference between the current frame and the first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

            # Dilate the thresholded image to fill in holes, then find contours on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop over the contours identified
            contourcount = 0
            for c in cnts:
                contourcount = contourcount + 1

                # If the contour is too small, ignore it
                if cv2.contourArea(c) < min_area:
                    continue
                _, frame_to_jpg=cv2.imencode('.jpg', frame)
                frame_bytes = frame_to_jpg.tobytes()
                client.publish(topics["topic_camera_feed"], frame_bytes)
                break

        frame_processing_time = time.time() - start_time
        if frame_processing_time < frame_delay:
            time.sleep(frame_delay - frame_processing_time)



def connect_mqtt()-> mqtt_client:
    global flag_auto
    global flag_realtime
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)


    def on_disconnect(client, userdata, flags, rc):
        global flag_auto
        global flag_realtime
        flag_auto=False
        flag_realtime=False
        
    # Set Connecting Client ID
    client = mqtt_client.Client(uid)
    client.on_connect = on_connect
    client.on_disconnect= on_disconnect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client,topics):
    for topic in topics:
        if topic == None:
            client.subscribe(topic)

def on_message(client, userdata, msg):
    global flag_auto,flag_realtime
    topic = msg.topic
    msg_string = msg.payload.decode()
    if topic==topics["topic_camera_realtime_feed_flag"] and msg_string=="ON":
        flag_realtime=True
    elif topic==topics["topic_camera_realtime_feed_flag"] and msg_string=="OFF":
        flag_realtime=False
    elif (topic == topics["topic_alarm_all"] or topic == topics["topic_alarm_all_minus_outside"] or topic ==topics["topic_alarm_room"]) and msg_string=="ON":
        flag_auto= True
    elif (topic == topics["topic_alarm_all"] and topic == topics["topic_alarm_all_minus_outside"] and topic ==topics["topic_alarm_room"]) and msg_string=="OFF":
        flag_auto= False
    elif topic == topics["topic_camera_feed"] and msg_string=="OFF":
        flag_realtime=False
    elif topic == topics["topic_camera_feed"] and msg_string=="ON":
        flag_realtime=True



def power_management(client):
    global power,sleep
    time.sleep(sleep)
    client.publish("power/used",float(3.6 * 10**6 *power*sleep))





def run():
    client = connect_mqtt()
    client.loop_start()
    subscribe(client,topics)
    client.on_message=on_message
    threads = []   
    t = continuous_threading.ContinuousThread(target=vCamera,args=(client,))
    threads.append(t)
    t.start()
    t= continuous_threading.PausableThread(target=power_management,args=(client, ))
    threads.append(t)
    t.start()


    while True:
        #Manual Changes
        user_input=input()
        try:
            exec(user_input,globals())
            save()  
        except :
            print("Command  failed ")
    


if __name__ == '__main__':
    run()
