import paho.mqtt.client as mqtt
import time, logging, datetime
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def loop():
    while True:
        check_timeouts()
        check_houses()
        process_queue()
        time.sleep(1)

@db_connect
def process_queue(session):
    queue = session.query(models.Queue)
    for q in queue:
        if open_valve(q.node.id):
            session.delete(q)

@db_connect
def check_houses(session):
    houses = session.query(models.House)
    for house in houses:
        if house.last_flush == None:
            house.last_flush = datetime.datetime(1,1,1)
        if (now() - house.last_flush).seconds > house.interval:
            logger.info("Initiating new flush for house '%s'" % house.name)
            for floor in house.floors:
                for flat in floor.flats:
                    for node in flat.nodes:
                        queue = models.Queue(node_id = node.id, added = now())
                        session.add(queue)
            house.last_flush = now()

@db_connect
def check_timeouts(session):
    nodes = session.query(models.Node)
    for node in nodes:
        if (now() - node.last_change).seconds > 10:
            if node.state_id == 2:
                publish_to_node(node.id, "open")
                set_state(node.id, 21)
                logger.warn("open retry 1 for node %s"%node.id)
            elif node.state_id == 21:
                publish_to_node(node.id, "open")
                logger.warn("open retry 2 for node %s"%node.id)
                set_state(node.id, 22)
            elif node.state_id == 4:
                publish_to_node(node.id, "close")
                logger.warn("close retry 1 for node %s"%node.id)
                set_state(node.id, 41)
            elif node.state_id == 41:
                publish_to_node(node.id, "close")
                logger.warn("close retry 2 for node %s"%node.id)
                set_state(node.id, 42)
            elif node.state_id in [22,42]:
                logger.warn("ping timeout for node %s"%node.id)
                set_state(node.id, 5)
                publish_to_node(node.id, "ping")
            elif node.state_id == 3:
                if node.flat.floor.house.length < (now() - node.last_change).seconds:
                    close_valve(node.id)
            elif node.state_id == 5:
                set_state(node.id, 9)
            elif node.state_id == 9:
                publish_to_node(node.id, "ping")

@db_connect
def on_message(mqttc, obj, msg, session):
    payload = msg.payload.decode()
    from_node = msg.topic.split('/')[2]
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
            elif payload == "pong":
                if old_state == 6:
                    set_state(from_node, 3, update_time = False)
                elif not old_state == 3:
                    set_state(from_node, 1)
            elif payload == "dropped":
                if old_state == 3:
                    set_state(from_node, 6, update_time = False)
                else:
                    set_state(from_node, 9)
            elif payload == "connected":
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
            set_state(new_node.id, 5)
            publish_to_node(from_node, "ping")

c = mqtt.Client("a")
c.connect("localhost")
c.on_message = on_message;
c.subscribe("painlessMesh/from/+")

c.loop_start()
loop()
