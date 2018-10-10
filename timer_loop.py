## -*- coding: utf-8 -*-

import time, logging, datetime, pdb
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
        if (now() - house.last_flush).seconds > house.interval and not house.interval == 0:
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
        #pdb.set_trace()
        logger.info("Checking node '%s' with state '%s'" % (node.id, node.state.name))
        if (now() - node.last_change).seconds > 10:
            if node.state_id == 2:
                publish_to_node(node.id, "open")
                set_state(node.id, 21)
                logger.warning("open retry 1 for node %s"%node.id)
            elif node.state_id == 21:
                publish_to_node(node.id, "open")
                logger.warning("open retry 2 for node %s"%node.id)
                set_state(node.id, 22)
            elif node.state_id == 4:
                publish_to_node(node.id, "close")
                logger.warning("close retry 1 for node %s"%node.id)
                set_state(node.id, 41)
            elif node.state_id == 41:
                publish_to_node(node.id, "close")
                logger.warning("close retry 2 for node %s"%node.id)
                set_state(node.id, 42)
            elif node.state_id in [22,42]:
                logger.warning("ping timeout for node %s"%node.id)
                set_state(node.id, 5)
                publish_to_node(node.id, "ping")
            elif node.state_id == 3:
                if node.flat.floor.house.length < (now() - node.last_change).seconds:
                    close_valve(node.id)
            elif node.state_id == 5:
                set_state(node.id, 9)
            elif node.state_id == 9:
                publish_to_node(node.id, "ping")


loop()
