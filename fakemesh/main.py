from models import *
import time, random
import paho.mqtt.client as mqtt

mqtt_server = "mqtt.booth" # use your ip/hostname here
c = mqtt.Client("python-fakemesh", clean_session = False)

def generate_send_func(c, topic):
    def send(node_id, msg):
        c.publish(topic + "/from/" + str(node_id), msg)
    return send

def get_gateway(topic):
    return Gateway(topic, generate_send_func(c, topic))

def on_message(mqttc, obj, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    gateway = topic.split('/')[0]
    if gateway in gateways:
        gateways[gateway].handle_msg(topic, payload)

c.connect(mqtt_server, 1883)
c.on_message = on_message;
c.subscribe("+/to/+", qos=1)


def on_log(client, userdata, level, buff):
    print(buff)

c.on_log = on_log

groups = []
gateways = {}
for letter in ["A","B","C","D","E","F"]:
    topic = "fake"+letter
    gateway= get_gateway(topic)
    gateways[topic] = gateway
    group = Group(gateway, 40)
    groups.append(group)

for group in groups:
    group.connect()
    # time.sleep(15)

c.loop_forever()
