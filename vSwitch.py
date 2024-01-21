import paho.mqtt.client as mqtt_client
import random
import time
import continuous_threading
import hashlib
import datetime
import argparse


flag="OFF"

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
variables = ['broker','name','port','room','power','idle_power','first_time']  # List of variable names


try:
    file = open(filename, 'a+')
    file.seek(0)
    content = file.read()
    file.close()

    if content:
        data = eval(content)  # Convert the content string to a dictionary
        print(data)
        data['first_time']=False
    else:
        print("File created successfully.")
        data = {}  # Create an empty dictionary to store the variables

        # Get input for each variable and store in the dictionary
        for variable in variables:
            data[variable] = None
            if variable=='port':
                data['port']=1883
            elif variable=='first_time':
                data['first_time']=True
        print(data)
        file = open(filename, 'w')  # Reopen the file in write mode
        file.write(str(data))  # Write the dictionary as a string to the file
        file.close()

    # Access the variables
    
    broker = str(data['broker'])
    port = int(data['port'])
    room_name = str(data['room'])
    name = str(data['name'])
    try:
        idle_power = int(data['idle_power'])
    except:
        idle_power=0  
    try:
        power = int(data['power'])
    except:
        power=0
    first_time=bool(data['first_time'])


except IOError:
    print("An error occurred while opening or creating the file.")
    exit()


def save():
    #Recall changed data
    filename='data.txt'
    variables = ['broker','name','port','room','power','idle_power','first_time'] 
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,name,port,room_name,power,idle_power,first_time]
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()



#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-n", "--name",required=True, type=str,help="Unique name for the switch")
    ap.add_argument("-p", "--port",type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,required=True, help="uid or unique name of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=0, help="Add power in W (per sec)")
    ap.add_argument("-iP", "--idle_power", type=int,default=0, help="Add power in W per s")

else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-n", "--name",type=str,help="Unique name for the switch")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,default=room_name , help="uid or unique name of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=power, help="Add power in W (per sec)")
    ap.add_argument("-iP", "--idle_power", type=int,default=idle_power, help="Add power in W (per s)")


args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["name"]!=None:
    name = args["name"]

if args["port"]!=None :
    port = args["port"]

if args["room"]!=None:
    room_name=args["room"]

try:
        idle_power = int(args["idle_power"])
except:
        idle_power=idle_power 
try:
        power = int(args["power"])
except:
        power=power


save()
    

def connect_mqtt()-> mqtt_client:
    global freezer
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

topics={
        "topic_switch_flag":   "switches/"+name+"/flag" 
    }

def subscribe(client: mqtt_client,topics):
    for topic in topics:
        if topic is not None:
            client.subscribe(topics[topic])
    
def on_message(client, userdata, msg):
        global flag ,idle_power
        topic = msg.topic
        msg_string = msg.payload.decode()
        if topic == topics["topic_switch_flag"]:
            if msg_string=="ON":
                flag=True
            elif msg_string=="OFF":
                flag=False



def switch(client):
    global flag,power,idle_power
    while True:
        time.sleep(1)
        while flag=="ON":
            time.sleep(1)
            client.publish("power/used",power)
            print("Switch is on")
        client.publish("power/used",idle_power)


def run():
    global flag
    client = connect_mqtt()
    client.loop_start()
    subscribe(client,topics)    
    t = continuous_threading.ContinuousThread(target=switch,args=(client,))
    t.start()
    while True:
        #Manual Changes
        user_input=input()
        try:
            flag2=flag
            exec(user_input,globals())
            if flag2!=flag and (flag =="ON"or flag == "OFF"):
                client.publish(topics["switches/"+name+"/flag"],"Switch turned manually " +flag)
            elif flag2==flag:
                print("Switch already " + flag)
            else:
                flag=flag2
            save()  
        except :
            print("Command  failed ")
    
    
    

if __name__ == '__main__':
    run()
