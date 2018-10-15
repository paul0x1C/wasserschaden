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
        house.gateway_state = True
        house.gateway_updated = now()
    if from_node == "gateway":
        pass
    else:
        from_node = int(from_node)
        if session.query(models.Node).filter(models.Node.id == from_node).count() > 0:
            node = session.query(models.Node).filter(models.Node.id == from_node).first()
            old_state = node.state_id
            if payload == "opening valve":
                set_state(from_node, 3)
            elif payload == "closing valve":
                set_state(from_node, 1)
                for listing in node.queue:
                    session.delete(listing)
            elif payload[:4] == "pong":
                if payload[-1:] == "1":
                    set_state(from_node, 3, update_time = False)
                else:
                    set_state(from_node, 1)
            elif payload == "dropped":
                if old_state == 3:
                    set_state(from_node, 6, update_time = False)
                else:
                    set_state(from_node, 9)
            elif payload[:3] == "con":
                if payload[-1:] == "1":
                    set_state(from_node, 3, update_time = False)
                    logger.info("Node %s reconnected and is still open")
                else:
                    set_state(from_node, 1)
        else:
            flat_id = session.query(models.Setting).filter(models.Setting.id == 1).first().state
            flat = session.query(models.Flat).filter(models.Flat.id == flat_id).first()
            print(from_node, flat.id, now())
            new_node = models.Node(id = from_node, flat_id = flat.id, state_id = 1, last_change = now(), reported_offline = False)
            logger.info("New node %s connect for the first time, adding to flat %s in house %s" % (from_node, flat.name, flat.floor.house.name))
            session.add(new_node)
            alert = models.Alert(added = now(), content="Node %s connected for the first time! Addded to flat '%s'" % (from_node, flat.name))
            session.add(alert)
            session.commit()

c = mqtt.Client("python-backend-", clean_session = False)
c.connect("localhost", 1883)
c.on_connect = on_connect
c.on_disconnect = on_disconnect
# c.reconnect_delay_set()
c.loop_forever()
