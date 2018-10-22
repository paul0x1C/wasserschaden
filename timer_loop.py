## -*- coding: utf-8 -*-

import time, logging, datetime, pdb, random
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

system_module = SystemModule(1, "timer_loop")

def loop():
    while True:
        system_module.update(1)
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
        last_physical_change = (now() - node.last_physical_change).seconds
        last_connection_change = (now() - node.last_connection_change).seconds
        last_physical_attempt = (now() - node.last_physical_attempt).seconds
        last_connection_attempt = (now() - node.last_connection_attempt).seconds
        if node.connection_state_id == 2:
            if node.connection_attemps == 0:
                if last_connection_change > 5:
                    publish_to_node(node, "ping")
                    add_connection_attempt(node)
            elif node.connection_attemps == 1:
                if last_connection_attempt > 10:
                    publish_to_node(node, "ping")
                    add_connection_attempt(node)
            elif node.connection_attemps > 1:
                if last_connection_attempt > 20:
                    set_connection_state(node, 3)
        elif node.connection_state_id == 3:
            if node.connection_attemps < 5:
                if last_connection_attempt > 100:
                    publish_to_node(node, "ping")
                    add_connection_attempt(node)
            else:
                if last_connection_attempt > 3600:
                    publish_to_node(node, "ping")
                    add_connection_attempt(node)
        if node.physical_state_id == 2:
            if node.physical_attemps == 0:
                if last_physical_change > 5:
                    publish_to_node(node, "open")
                    add_physical_attempt(node)
            elif node.physical_attemps < 3:
                if last_physical_attempt > 10:
                    publish_to_node(node, "open")
                    add_physical_attempt(node)
            else:
                set_connection_state(node, 2)
                set_physical_state(node, 1)
                publish_to_node(node, "ping")
        elif node.physical_state_id == 4:
            if node.physical_attemps == 0:
                if last_physical_change > 5:
                    publish_to_node(node, "close")
                    add_physical_attempt(node)
            elif node.physical_attemps < 3:
                if last_physical_attempt > 10:
                    publish_to_node(node, "close")
                    add_physical_attempt(node)
            else:
                set_connection_state(node, 2)
                set_physical_state(node, 1)
                publish_to_node(node, "ping")
        elif node.physical_state_id == 3:
            if node.flat.floor.house.length <= last_physical_change:
                publish_to_node(node, "close")
                set_physical_state(node, 4)
loop()
