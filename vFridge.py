import paho.mqtt.client as mqtt_client
import random
import time
import continuous_threading
import hashlib
import datetime
import argparse
import ast


room_volume=0
zones=0
desired_Temperature=[]
zone_Temperature=[] # initialization value
freezer =[]
power_of_the_zone=[]
power_of_the_zone_idle=[]
zone_volume=[]
sleep=10


def init_zones():
    global zones ,zone_Temperature,desired_Temperature ,power_of_the_zone,zone_volume,power_of_the_zone_idle,freezer
    zone_Temperature.clear()
    desired_Temperature.clear()
    zone_volume.clear()
    freezer.clear()
    power_of_the_zone_idle.clear()

    for i in range(zones):

        zone_Temperature.append(random.randint(16,24))
        desired_Temperature.append(9000)
        power_of_the_zone.append(0)
        volume = float(input("Volume for the zone "+str(i)+ " in Litres:\t"))
        volume= float(volume/1000) #convert to m^3
        zone_volume.append(volume)
        power_of_the_zone_idle.append(1) # place holder
        freezer.append(False)
    save()






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
variables = ['broker','port','name','power','first_time','room_name','zones','desired_Temperature','zone_volume','power_of_the_zone_idle','sleep','idle_power'] 


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
    name = str(data['name'])
    try:
        power=int(data['power'])
    except:
        power=350
    try:
        idle_power=int(data['idle_power'])
    except:
        idle_power=0    
    room_name=str(data['room_name'])

    first_time=bool(data['first_time'])

    try:
        sleep=int(data['sleep'])
    except:
        sleep=10
    try:
        desired_Temperature=ast.literal_eval(data['desired_Temperature'])
        zone_volume=ast.literal_eval(data['zone_volume'])
        power_of_the_zone_idle=ast.literal_eval(data['power_of_the_zone_idle'])
    except:
        pass

    try:
        zones= int(data['zones'])
    except:
        zones=None
    # Perform any necessary operations with the variables
except IOError:
    print("An error occurred while opening or creating the file.")
    exit()


def save():
    #Recall changed data
    global broker,port,name,power,first_time,room_name,zones,desired_Temperature,zone_volume,power_of_the_zone_idle,sleep,idle_power
    filename='data.txt'
    variables = ['broker','port','name','power','first_time','room_name','zones','desired_Temperature','zone_volume','power_of_the_zone_idle','sleep','idle_power'] 
    data_to_save = {}  # Create an empty dictionary to store the variables
    variables_check = [broker,port,name,power,first_time,room_name,zones,desired_Temperature,zone_volume,power_of_the_zone_idle,sleep,idle_power]
    # Get input for each variable and store in the dictionary
    for counter in range(len(variables)):
        if variables[counter]=='zone_Temperature' or variables[counter]=='desired_Temperature' or variables[counter]=='zone_volume' or variables[counter]=='power_of_the_zone_idle' :
            data_to_save[variables[counter]] = str(variables_check[counter])
        else:
            data_to_save[variables[counter]] = variables_check[counter]
    file = open(filename, 'w')  # Reopen the file in write mode
    file.write(str(data_to_save))  # Write the dictionary as a string to the file
    file.close()



#GET ARGUMENTS
ap = argparse.ArgumentParser()

if first_time:
    ap.add_argument("-b", "--broker",required=True, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",type=int,default=1883 , help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,help="name of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=350, help="Add power in kWh/y")
    ap.add_argument("-iP", "--idle_power", type=int,default=0, help="Add idle power in W")
    ap.add_argument("-z", "--zones",required=True,help="Number of zones")
    ap.add_argument("-s", "--sleep", type=int,default=10, help="number of seconds between each sleep of the fridge")
    ap.add_argument("-n", "--name",required=True, type=str,help="Unique name for the device")
else:
    ap.add_argument("-b", "--broker",default=broker, type=str,help="Broker IPv4")
    ap.add_argument("-p", "--port",default=port,type=int,help="Broker listening port")
    ap.add_argument("-r", "--room",type=str,default=room_name,help="id of the room that the device is located")
    ap.add_argument("-P", "--power", type=int,default=power, help="Add power in kWh/y")
    ap.add_argument("-z", "--zones", default=zones,help="Number of zones")
    ap.add_argument("-s", "--sleep", type=int,default=sleep, help="number of seconds between each sleep of the Fridge")
    ap.add_argument("-n", "--name",default=name ,type=str,help="Unique name for the device")

args = vars(ap.parse_args())

#GET CHANGES INTO THE VARIABLES
if args["broker"]!=None:
    broker = args["broker"]

if args["sleep"]!=None:
    sleep = args["sleep"]

if args["port"]!=None :
    port = args["port"]
try:
    power = int(args["power"])
except:
    power=power


try:
    idle_power = int(args["idle_power"])
except:
    idle_power=idle_power

if args["room"]!=None:
    room_name=args["room"]

if args["name"]!=None:
    name=args["name"]

if args['zones']!=zones:
    try:
        zones= int(args["zones"])
        init_zones()
    except:
        zones=zones
        for i in range(zones):
            freezer.append(False)
            zone_Temperature.append(random.randint(16,24))

else: 
    for i in range(zones):
        freezer.append(False)
        zone_Temperature.append(random.randint(16,24))
    



save()




def zoneTemperature(freezer,zone):
    global zone_volume,sleep
    if freezer==True:
        r=1.204 #density of air for 20C
        cp=1007    #Specific heat in constant pressure for air on 20C
        # DISCLOSURE: For simpler calculation we assume that r and cp are constants
        freezer_deviation=-(frezer_power()/(r*cp*zone_volume[zone]))
	deviation=random.uniform(0,freezer_deviation/2)
    else:
        freezer_deviation=0
	deviation=random.uniform(0,0.002)

    zone_Temperature[zone]=zone_Temperature[zone]+sleep*(deviation+freezer_deviation)
    return zone_Temperature[zone]

    

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



def make_decision(zone):
    global desired_Temperature , zone_Temperature
    if desired_Temperature[zone] +0.1 < zone_Temperature[zone]:
        freezer[zone]=True #running
    elif desired_Temperature[zone]-0.1 > zone_Temperature[zone]:
        freezer[zone]=False #not running
    return freezer[zone]



def subscribe(client: mqtt_client,topics):
    global desired_Temperature
    for topic in topics:
        if topic is not None:
            client.subscribe(topics[topic])
            print(topics[topic])


def on_message(client, userdata, msg):
        global desired_Temperature
        topic = msg.topic
        msg_string = msg.payload.decode()
        parts = topic.split('/')
        flag=parts[3]
        if flag == "dtmp":
            zone=parts[2]
            i=int(zone[-1])
            desired_Temperature[i]=int(msg_string)
            print(zone + ' dtmp : ' + str(desired_Temperature[i]))
    

def power_management(client):
    global power,sleep,idle_power
    time.sleep(sleep)
    for i in range(zones):
        if freezer[i]==True:
            client.publish("power/used",sleep*power*0.1141552511415525)
            flag=True
            break
    if flag==True:
         client.publish("power/used",sleep*idle_power)


def zoning(client,zone):
    global desired_Temperature ,name ,zone_Temperature,sleep
    
    topics={
        "topic_zone_desired_temperature":   "fridge/"+str(name)+"/zone"+str(zone)+"/dtmp"
    }
    subscribe(client,topics)
    
    while True:
        
        zone_Temperature[zone] = zoneTemperature(make_decision(zone),zone)
        client.publish("fridge/"+str(name)+"/zone"+str(zone)+"/tmp",zone_Temperature[zone])
        time.sleep(sleep)


def frezer_power():
    global freezer,power
    x=0
    for i in freezer:
        if i ==True:
            x+=1

    return (power*0.0001086)/x




def run():
    global zones,sleep
    client = connect_mqtt()
    #argparse zones 
    threads = []    
    client.loop_start()
    while True:
        threads.clear()
        # Create and start the threads
        
        for zone in range(zones):
            t = continuous_threading.PausableThread(target=zoning,args=(client, zone))
            threads.append(t)
            t.start()
        t= continuous_threading.PausableThread(target=power_management,args=(client, ))
        threads.append(t)
        t.start()

        client.on_message = on_message
        while True:
            #Manual Changes
            user_input=input()
            try:
                zones2=zones
                exec(user_input,globals()) 
                try:
                    zones=int(zones)
                    if zones2!=zones:
                        for thread in threads:
                            thread.stop()    
                        print("changing the number of the zones may lead into an exception but the program will continue working")
                        time.sleep(10)
                        init_zones()
                        save()
                        threads.clear()    
                        break
                    save()
                except:
                    save()
    
                
                
            except :
                print("Command  failed ")
            
        
    
    

if __name__ == '__main__':
    run()
