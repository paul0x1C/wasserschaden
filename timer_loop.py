## -*- coding: utf-8 -*-

import time, logging, datetime, pdb, random, sys, traceback
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
        time.sleep(1)
        try:
            system_module.update(1)
            check_timeouts()
            process_queue()
            check_houses()
        except:
            e = traceback.format_exc()
            logger.error(e)
            add_alert(e)

@db_connect
def add_alert(alert_text, session):
    alert_text += "exception in timer_loop:\n"
    alert = models.Alert(content = alert_text, added = now())
    session.add(alert)

@db_connect
def process_queue(session):
    logger.info("checking que")
    queue = session.query(models.Queue)
    for q in queue:
        if q.node.open_valve():
            session.delete(q)
    logger.info("done checking que")

@db_connect
def check_houses(session):
    logger.info("checking house timeouts")
    houses = session.query(models.House)
    for house in houses:
        if house.last_flush == None:
            house.last_flush = datetime.datetime(1,1,1)
        if (now() - house.last_flush).seconds > house.interval and not house.interval == 0:
            logger.info("Initiating new flush for house '%s'" % house.name)
            for floor in house.floors:
                for flat in floor.flats:
                    for node in flat.nodes:
                        queue = models.Queue(node_id = node.id, house_id = house.id, added = now())
                        session.add(queue)
            house.last_flush = now()
        if house.locked and (now() - house.locked_since).seconds > 120:
            house.unlock()
            logger.warning("Lock for house %s timed out!" % house.id)
    logger.info("done checking houses")

@db_connect
def check_timeouts(session):
    nodes = session.query(models.Node).filter((models.Node.physical_state_id > 1) | (models.Node.connection_state_id > 1))
    logger.info("checking node timeouts")
    for node in nodes:
        last_physical_change = (now() - node.last_physical_change).seconds
        last_connection_change = (now() - node.last_connection_change).seconds
        last_physical_attempt = (now() - node.last_physical_attempt).seconds
        last_connection_attempt = (now() - node.last_connection_attempt).seconds
        if node.connection_state_id == 2:
            if node.connection_attemps == 0:
                if last_connection_change > 5:
                    node.send_mqtt_msg("ping")
                    node.add_connection_attempt(session)
            elif node.connection_attemps == 1:
                if last_connection_attempt > 10:
                    node.send_mqtt_msg("ping")
                    node.add_connection_attempt(session)
            elif node.connection_attemps > 1:
                if last_connection_attempt > 20:
                    node.set_connection_state(3)
        elif node.connection_state_id == 3:
            if node.connection_attemps < 5:
                if last_connection_attempt > 100:
                    node.send_mqtt_msg("ping")
                    node.add_connection_attempt(session)
            else:
                if last_connection_attempt > 3600:
                    node.send_mqtt_msg("ping")
                    node.add_connection_attempt(session)
        if node.physical_state_id == 2:
            if node.physical_attemps == 0:
                if last_physical_change > 5:
                    node.send_mqtt_msg("open")
                    node.add_physical_attempt()
            elif node.physical_attemps < 3:
                if last_physical_attempt > 10:
                    node.send_mqtt_msg("open")
                    node.add_physical_attempt()
            else:
                node.set_connection_state(2)
                node.set_physical_state(1)
                node.send_mqtt_msg("ping")
        elif node.physical_state_id == 4:
            if node.physical_attemps == 0:
                if last_physical_change > 5:
                    node.send_mqtt_msg("close")
                    node.add_physical_attempt()
            elif node.physical_attemps < 3:
                if last_physical_attempt > 10:
                    node.send_mqtt_msg("close")
                    node.add_physical_attempt()
            else:
                node.set_connection_state(2)
                node.set_physical_state(1)
                node.send_mqtt_msg("ping")
        elif node.physical_state_id == 3:
            if node.flat.floor.house.duration <= last_physical_change:
                node.close_valve()
    logger.info("done checking nodes")
loop()
