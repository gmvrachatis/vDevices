import paho.mqtt.client as mqtt_client
import random
import time
import argparse
import datetime
import hashlib
import continuous_threading


power=0

#CREATE UNiQuE ID
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
variables = ['broker','port','power','power_management','camera_recorder','timer','first_time']  # List of variable names

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
            elif variable=='first_time':
                data['first_time']=True

        file = open(filename, 'w')  # Reopen the file in write mode
        file.write(str(data))  # Write the dictionary as a string to the file
        file.close()

    # Access the variables
    broker = str(data['broker'])
    port = int(data['port'])
    power_management = bool(data['power_management'])
    camera_recorder = bool(data['camera_recorder'])
    try:
        timer=int(data['timer'])
    except:
        timer=60
    first_time=bool(data['first_time'])
    # Perform any necessary operations with the variables

except IOError:
    print("An error occurred while opening or creating the file.")
    exit()







#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",type=int,default=1883, help="Broker listening port")
    ap.add_argument("-Pm", "--power_management", type=bool, default=False, help="Add power in BTU per h")
    ap.add_argument("-c", "--camera_recorder", type=bool, default=False,help="Add power in W/h")
    ap.add_argument("-t", "--timer", type=int, default=60,help="Timer that counts when to display power usage")
else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-Pm", "--power_management", type=bool, default=False, help="Add power in BTU per h")
    ap.add_argument("-c", "--camera_recorder", type=bool, default=False,help="Add power in W/h")
    ap.add_argument("-t", "--timer", type=int, default=timer,help="Timer that counts when to display power usage")


args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["port"]!=None :
    port = args["port"]

if args["power_management"]!=None:
    power_management=args["power_management"]

if args["camera_recorder"]!=None:
    camera_recorder=args["camera_recorder"]

if args["timer"]!=None:
    timer=int(args["timer"])

def save():
    #Recall changed data
    filename='data.txt'
    variables = ['broker','port','power_management','camera_recorder','timer','first_time']
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,port,power_management,camera_recorder,timer,first_time]
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()

save()





def subscribe_to_power(client: mqtt_client):
    client.subscribe("power/used")

def subscribe_to_feed(client: mqtt_client):
    client.subscribe("cameras/+/+/trigered")
    client.subscribe("cameras/outside/+/trigered")
    client.subscribe("cameras/+/+/feed" )
    client.subscribe("cameras/outside/+/feed")




def on_message(client, userdata, msg):
        global power 
        topic = msg.topic
        

        if topic== "power/used":
	    msg_string = msg.payload.decode()
            power += float(msg_string)
        else:
            print("frame_received")

def connect_mqtt()-> mqtt_client:

    def on_connect(client, userdata, flags, rc):

        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
        
    # Set Connecting Client ID
    client = mqtt_client.Client(uid)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def vcontroller(client) :
    global camera_recorder ,power_management,timer,power
    while True:
        
        if camera_recorder:
            try:
                subscribe_to_feed(client)
            except:
                print("No Camera feed found")
            
        if power_management:
            subscribe_to_power(client)
            print("Energy Consumed in "+str(timer)+" seconds: "+str(power)+ " J")
            power=0
        
        time.sleep(timer)



def run():  
    global flag
    client = connect_mqtt()
    client.on_message = on_message 
       
    t = continuous_threading.ContinuousThread(target=vcontroller, args=(client,))
    t.start()
    client.loop_start()
    
    while True:
        #Manual Changes
        user_input=input()
        try:
            exec(user_input,globals())
            save()
        except :
            print("Command  failed "+str(globals()))
    
    



if __name__ == '__main__':
    run()
