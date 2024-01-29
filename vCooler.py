import paho.mqtt.client as mqtt_client
import random
import time
import argparse
import datetime
import hashlib
import continuous_threading

thermostat_flag =False
flag=False
timer=10

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
variables = ['broker','port','room','power','idle_power','timer','first_time']  # List of variable names

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
    room_name = str(data['room'])
    try:
        BTUc = int(data['power'])
    except:
        BTUc = 9000
    try:
        idle_power = int(data['idle_power'])
    except:
        idle_power= 0
    first_time=bool(data['first_time'])
    # Perform any necessary operations with the variables
    try:
        timer=int(data['timer'])
    except:
        timer=10

except IOError:
    print("An error occurred while opening or creating the file.")
    exit()







#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",type=int,default=1883, help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,required=True ,help="id of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=9000, help="Add power in BTU per h")
    ap.add_argument("-iP", "--idle_power", type=int,default=0, help="Add power in W/h")
    ap.add_argument("-t", "--timer", type=int,default=10, help="Timer that counts when to send power usage")
else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,default=room_name,help="id of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=BTUc, help="Add power in W/s")
    ap.add_argument("-iP", "--idle_power", type=int,default=idle_power, help="Add power in W/s")
    ap.add_argument("-t", "--timer", type=int,default=timer, help="Timer that counts when to send power usage")

args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["port"]!=None :
    port = args["port"]

if args["power"]!=None:
    BTUc=args["power"]

if args["room"]!=None:
    room_name=args["room"]

if args["power"]!=None:
    power=args["power"]

if args["idle_power"]!=None:
    idle_power=args["idle_power"]

if args["timer"]!=None:
    timer=args["timer"]

def save():
    #Recall changed data
    filename='data.txt'
    variables = ['broker','port','room','power','idle_power','timer','first_time']
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,port,room_name,BTUc,idle_power,timer,first_time]
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()

save()



topics={    
            "topic_room_thermostat": room_name+"/thermostat/flag",
            "topic_coolers":room_name+"/thermostat/coolers/flag"
       }








def subscribe(client: mqtt_client,topics):
    for topic in topics:
        if topic is not None:
            client.subscribe(topics[topic])
    
def on_message(client, userdata, msg):
        global BTUc, flag ,idle_power ,thermostat_flag ,room_name
        topic = msg.topic
        msg_string = msg.payload.decode()
        if topic == topics["topic_room_thermostat"]:
            client.publish(room_name+"/thermostat/heaters/btu",BTUc)
        elif topic == topics["topic_coolers"]:
            if msg_string=="ON":
                flag=True
            elif msg_string=="OFF":
                flag=False



def connect_mqtt()-> mqtt_client:

    def on_connect(client, userdata, flags, rc):

        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    def on_disconnect(client, userdata, flags, rc):

        client.publish(topics["power"], -power)
        client.publish(topics["idle_power"], -idle_power)
        
    # Set Connecting Client ID
    client = mqtt_client.Client(uid)
    client.on_connect = on_connect
    client.on_disconnect= on_disconnect
    client.connect(broker, port)
    return client

def cooler(client) :
    global flag ,BTUc,idle_power,timer
    sleep_counter=0
    power=0
    while True:
      
        time.sleep(1)
        if flag:
            #generate_heat
            power+=BTUc*3.412141633/3600
            print("working")
        else:
            #go idle
            power+=idle_power
            print("idle")
        sleep_counter+=1
        if sleep_counter==timer:
            client.publish("power/used", power)
            sleep_counter=0
            power=0

def run():
    global flag
    client = connect_mqtt()
    subscribe(client,topics)
    client.on_message = on_message    
    t = continuous_threading.ContinuousThread(target=cooler, args=(client,))
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

    
    



if __name__ == '__main__':
    run()
