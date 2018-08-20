import paho.mqtt.client as mqttClient
import time, datetime, os

filename = "log.csv"
last_requested = 0
response = True

valves = [2485890083, 2485889417, 2485890828, 2138497445, 2485891313]

topline = "Zeit"
for valve in valves:
    topline += ","
    topline += str(valve)
with open(filename, "w") as file:
    file.write(topline + "\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    global last_requested, response
    x,type,valve = message.topic.split("/")
    msg = message.payload.decode()
    if type == "to":
        if not response:
            generate_csv_line(int(last_requested), "no connection")
        last_requested = int(valve)
        response = False
    else:
        print("Valve %s: %s" % (valve, msg))
        if not valve == "gateway":
            generate_csv_line(int(valve), msg)
            if int(valve) == last_requested:
                response = True

def generate_csv_line(valve, msg):
    line = datetime.datetime.now().strftime("%H:%M:%S")
    for i in range(valves.index(valve)):
        line += ","
    line += ","
    line += msg
    for i in range(len(valves) - valves.index(valve) - 1):
        line += ","
    save_line(line)


def save_line(line):
    with open(filename, "a") as file:
        file.write(line + "\n")


Connected = False   #global variable for the state of the connection

sub_prefix = "painlessMesh/#"
broker_address= "localhost"  #Broker address
port = 1883                         #Broker port

client = mqttClient.Client("Python")               #create new instance
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback

client.connect(broker_address, port=port)          #connect to broker

client.loop_start()        #start the loop

while Connected != True:    #Wait for connection
    time.sleep(0.1)

client.subscribe(sub_prefix)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
