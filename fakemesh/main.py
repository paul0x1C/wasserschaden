from models import *
import time, random
import paho.mqtt.client as mqtt

mqtt_server = "mos.fritz.box" # use your ip/hostname here
c = mqtt.Client("python-fakemesh", clean_session = False)

def generate_send_func(c, topic):
    def send(node_id, msg):
        c.publish(topic + "/from/" + str(node_id), msg)
    return send


gateway = Gateway("fake", generate_send_func(c, "fake"))

def on_message(mqttc, obj, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    gateway.handle_msg(topic, payload)

c.connect(mqtt_server, 1883)
c.on_message = on_message;
c.subscribe("+/to/+", qos=1)


def on_log(client, userdata, level, buff):
    print(buff)

c.on_log = on_log

groups = []
for i in range(10):
    group = Group(gateway, 30)
    groups.append(group)

for group in groups:
    group.connect()
    time.sleep(0)

c.loop_forever()
