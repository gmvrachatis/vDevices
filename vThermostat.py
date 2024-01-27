import paho.mqtt.client as mqtt_client
import random
import time
import argparse
import datetime
import hashlib
import continuous_threading



#starting_tmp
desired_Temperature = 999
env_temperature = 25
flag_mode="OFF"
BTUh=0 #For heaters
BTUc=0 #For coolers
sleep =60
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

except IOError:
    print("An error occurred while opening or creating the file.")
    exit()

thermostat_id = uid



#create data storing file and reading from it
filename = 'data.txt'
variables = ['broker','port','room','room_volume','power','sleep','first_time']  # List of variable names


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
            if variable=='port':
                data['port']=1883
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
        sleep = int(data['sleep'])
    except:
        sleep = 10 
    try:
        room_volume= int(data['room_volume'])
    except:
        room_volume=40
    try:
        power = int(data['power'])
    except:
        power=0
    first_time=bool(data['first_time'])


except IOError:
    print("An error occurred while opening or creating the file.")
    exit()







#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",default=1883,type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,required=True ,help="uid or unique name of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=0, help="Add power in W (per sec)")
    ap.add_argument("-s", "--sleep", type=int,default=10, help="number of seconds for sleep of the thermostat")
    ap.add_argument("-v", "--volume", type=int,default=20, help="Add Room volume for temperature changes calculation (in m^3)")
else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,default=room_name , help="uid or unique name of the room that the device is located")
    ap.add_argument("-P", "--power", type=int, help="Add power in W (per sec)")
    ap.add_argument("-s", "--sleep", type=int,default=sleep, help="number of seconds for sleep of the thermostat")
    ap.add_argument("-v", "--volume", type=int,default=room_volume, help="Add Room volume for temperature changes calculation (in m^3)")


args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["sleep"]!=None:
    sleep = args["sleep"]

if args["port"]!=None :
    port = args["port"]

if args["room"]!=None:
    room_name=args["room"]

if args["volume"]!=None:
    room_volume=args["volume"]

try:
    power=int(args["power"])
except:
    power=power

topics={    
            "topic_mode":room_name+"/thermostat/mode",
            "topic_Desired_Temperature":room_name+"/thermostat/dtmp",
            "topic_heat_working_power":room_name+"/thermostat/heaters/btu",
            "topic_cold_working_power":room_name+"/thermostat/coolers/btu"
            }

def save():
    #Recall changed data
    filename='data.txt'
    variables =  ['broker','port','room','room_volume','power','sleep','first_time']  
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,port,room_name,room_volume,power,sleep,first_time]
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()


save()
        


def subscribe(client: mqtt_client,topics):
    global desired_Temperature
    for topic in topics:
        if topic is not None:
            client.subscribe(topics[topic])
            print(topics[topic])


def on_message(client, userdata, msg):
    global flag_mode,desired_Temperature,BTUh,BTUc
    topic = msg.topic
    msg_string = msg.payload.decode()
        
    if topic==topics["topic_mode"] and msg_string=="OFF":
            flag_mode="OFF"

    elif topic==topics["topic_mode"] and msg_string=="ON":
            flag_mode="ON"

    elif topic == topics["topic_Desired_Temperature"] :
            desired_Temperature = int(msg_string)

    elif topic == topics["topic_heat_working_power"]:
            BTUh+=int(msg_string)
            
    elif topic == topics["topic_cold_working_power"]:
            BTUc+=int(msg_string)


    print("Received at"+ str(topic)+" the message "+ msg_string)




def connect_mqtt()-> mqtt_client:
    global BTUc ,BTUh
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            
    def on_disconnect(client, userdata, flags, rc):
        print("Disconnected")
        global BTUc ,BTUh
        while rc!=0:
            BTUc=0
            BTUh=0
            client.publish(room_name+"/thermostat/flag","Syncing new devices...")
        
    # Set Connecting Client ID
    client = mqtt_client.Client(thermostat_id)
    client.on_connect = on_connect
    client.on_disconnect= on_disconnect
    client.connect(broker, port)
    return client




def heat():
    global BTUh ,room_volume
    r=1.204 #density of air for 20C
    cp=1007    #Specific heat in constant pressure for air on 20C
    # DISCLOSURE: For simpler calculations we assume that r and cp are constants
    btuh_to_watt=BTUh *0.293 # BTU per h to BTU per s
    dt=btuh_to_watt/(r*cp*room_volume)
    return dt

def cold():
    global BTUc ,room_volume
    
    r=1.204 #density of air for 20C
    cp=1005    #Specific heat in constant pressure for air on 20C
    # DISCLOSURE: For simpler calculation we assume that r and cp are constants
    BTUc_to_watt=BTUc *0.293
     # BTU to KW
    dt=BTUc_to_watt/(r*cp*room_volume)
    return -dt


def enviromental_temperature(ac_changes,client):
    global env_temperature
    if -10 < env_temperature < 50:
        weather_deviation = (random.uniform(0, 1) - 0.5)/1000000000
        env_temperature += weather_deviation + ac_changes
    else:
        env_temperature = random.randint(15,25)
        print("Temperature have been reset")
    client.publish(room_name+"/thermostat/tmp",env_temperature)
    print(room_name+"/thermostat/tmp"+" = "+ str(env_temperature))


def decide_action(client):
    global sleep,env_temperature,flag_mode,desired_Temperature
    if flag_mode == "ON":
        if  env_temperature < desired_Temperature -0.05:
            client.publish(room_name+"/thermostat/coolers/flag", "OFF")  # heat
            client.publish(room_name+"/thermostat/heaters/flag", "ON")
            print("cold = off\n heat = on")
            enviromental_temperature(sleep*heat(),client)
        elif env_temperature > desired_Temperature+0.05:
            client.publish(room_name+"/thermostat/heaters/flag", "OFF")  # cold
            client.publish(room_name+"/thermostat/coolers/flag", "ON")
            print("cold = on \n heat = off")
            enviromental_temperature(sleep*cold(),client)
        else:
            print("idle")
            client.publish(room_name+"/thermostat/heaters/flag", "OFF")  # NONE
            client.publish(room_name+"/thermostat/coolers/flag", "OFF")  # NONE
            enviromental_temperature(0,client)
        client.publish("power/used",sleep*power)
    elif flag_mode == "OFF":
        print("idle")
        client.publish(room_name+"/thermostat/heaters/flag", "OFF")  # NONE
        client.publish(room_name+"/thermostat/coolers/flag", "OFF")  # NONE
        enviromental_temperature(0,client)


def thermostat(client):
    global sleep
    client.publish(room_name+"/thermostat/flag","Syncing new devices...")
    time.sleep(10)
    while True:
        time.sleep(sleep)
        decide_action(client)

def run():
    global BTUc,BTUh
    client = connect_mqtt()
    client.loop_start()
    subscribe(client,topics)
    client.on_message = on_message
    t = continuous_threading.ContinuousThread(target=thermostat, args=(client,))
    t.start()
    while True:
        #Manual Changes

        user_input=input()

        if user_input=="sync":
            BTUc=0
            BTUh=0
            client.publish(room_name+"/thermostat/flag","Manual Syncing new devices...")
        else:    
            try: 
            
                exec(user_input,globals())
            
                save()
            except :
                print("Command  failed ")


if __name__ == '__main__':
    run()
