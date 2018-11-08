## -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import time, logging, datetime
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

system_module = SystemModule(2, "mqtt_loop")
system_module.update(1)

def on_connect(client, userdata, flags, rc):
    logger.info("MQTT connected")
    c.on_message = on_message;
    c.subscribe("+/from/+", qos=1)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("Unexpected MQTT disconnection. Will auto-reconnect")

@db_connect
def on_message(mqttc, obj, msg, session):
    system_module.update(1)
    payload = msg.payload.decode()
    bridge = msg.topic.split('/')[0]
    from_node = msg.topic.split('/')[2]
    try:
        house = session.query(models.House).filter(models.House.mqtt_topic == bridge).one()
    except:
        logger.warning("Got message from not matching bridge '%s'" % bridge)
    else:
        house.gateway_updated = now()
        if from_node == "gateway":
            if payload == "dead":
                house.gateway_state = False
                logger.info("gateway '%s' went offline" % bridge)
        else:
            house.gateway_state = True
            from_node = int(from_node)
            if session.query(models.Node).filter(models.Node.id == from_node).count() > 0: # check if node exists
                node = session.query(models.Node).filter(models.Node.id == from_node).first()
                if payload == "opening valve":
                    node.set_physical_state(3)
                elif payload == "closing valve":
                    node.set_physical_state(1)
                    for listing in node.queue:
                        session.delete(listing)
                elif payload[:4] == "pong":
                    node.set_connection_state(1)
                    if payload[-1:] == "1" and not node.physical_state_id == 3:
                        node.set_physical_state(3)
                    elif payload[-1:] == "0" and not node.physical_state_id == 1:
                        node.set_physical_state(1)
                elif payload == "dropped":
                    node.set_connection_state(3)
                elif payload[:3] == "con":
                    node.set_connection_state(1)
                    if payload[-1:] == "1" and not node.physical_state_id == 3:
                        node.set_physical_state(3)
                    elif payload[-1:] == "0" and not node.physical_state_id == 1:
                        node.set_physical_state(1)
            else:
                flat = house.new_node_flat
                if flat: # check if flat is set (== not None)
                    new_node = models.Node(id = from_node, flat_id = flat.id,
                                        connection_state_id = 1, physical_state_id = 1,
                                        reported_offline = False,
                                        last_physical_change = now(),
                                        last_connection_change = now(),
                                        last_physical_attempt = now(),
                                        last_connection_attempt = now(),
                                        house_id = flat.floor.house_id
                                    )
                    logger.info("New node %s connect for the first time, adding to flat %s in house %s" % (new_node, flat, new_node.house))
                    session.add(new_node)
                    # alert = models.Alert(added = now(), content="Node %s connected for the first time! Addded to flat '%s'" % (from_node, flat.name))
                    # session.add(alert)
                else:
                    logger.warn("Couldn't add node %s because new_node_flat for house %s is not set" % (from_node, house))


def on_log(client, userdata, level, buff):
    print(level)
    logger.warning(buff)

c = mqtt.Client("python-backend-", clean_session = False)
c.connect("localhost", 1883)
c.on_log = on_log
c.on_connect = on_connect
c.on_disconnect = on_disconnect
# c.reconnect_delay_set()
c.loop_forever()
