## -*- coding: utf-8 -*-

import time, logging, datetime, pdb, random, sys, traceback
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

system_module = SystemModule(1, "timer_loop")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting timer_loop")

def loop():
    while True:
        time.sleep(1)
        try:
            system_module.update(1)
            check_nodes()
            process_queue()
            check_houses()
        except:
            e = traceback.format_exc()
            logger.error(e)
            add_alert("Exception in timer loop!", 5)

@db_connect
def process_queue(session):
    logger.debug("checking que")
    houses = session.query(models.House)
    for house in houses:
        if not house.locked:
            for q in house.queue:
                if q.node.open_valve():
                    session.delete(q)
                    break;
    logger.debug("done checking que")

@db_connect
def check_houses(session):
    logger.debug("checking houses")
    houses = session.query(models.House)
    for house in houses:
        logger.debug("checking %s" % house)
        if house.last_flush == None: # make sure last_flush is set
            house.last_flush = datetime.datetime(1,1,1)

        if (now() - house.last_flush).seconds > house.interval and not house.interval == 0: # check if house needs to be flushed
            logger.info("Initiating new flush for %s" % house)
            add_alert("Initiating new flush for %s" % house, 1)
            for node in house.nodes:
                if session.query(models.Queue).filter(models.Queue.node_id == node.id).count() == 0: #check whether node is already queued
                    que = models.Queue(node_id = node.id, house_id = house.id, added = now())
                    session.add(que)
                else:
                    logger.warning("%s was already queued" % node)
                    add_alert("Tried to add a node to {}'s queue, but it was already in the queue".format(house), 2)
            house.last_flush = now()

        if house.locked and (now() - house.locked_since).seconds > 150: # check if house is locked for a too long time
            house.unlock()
            logger.warning("Lock for house %s timed out!" % house)

        last_gateway_change = (now() - house.gateway_updated).seconds
        if last_gateway_change > 60: # ping gateway if it has not send anything for longer than 60s
            send_mqtt_msg(house.mqtt_topic + "/to/gateway", "ping")
            if house.gateway_state == 1:
                if last_gateway_change > 90: # set gateway to disconnected when it's not responding for >90s
                    house.gateway_state = 2
                    logger.info("gateway in {} is not responding".format(house))
                    add_alert("gateway in {} is not responding".format(house), 2)
            else:
                if last_gateway_change > 3600 and house.gateway_state == 2: # higher priority alert after 1h
                    house.gateway_state = 3
                    logger.warning("gateway in {} is not responding since an hour".format(house))
                    add_alert("gateway in {} is not responding since an hour".format(house), 3)



    logger.debug("done checking houses")

@db_connect
def check_nodes(session):
    nodes = session.query(models.Node).filter((models.Node.physical_state_id > 1) | (models.Node.connection_state_id > 1))
    logger.debug("checking node timeouts")
    for node in nodes:
        if node.house.gateway_state == 1:
            last_physical_change = (now() - node.last_physical_change).seconds
            last_connection_change = (now() - node.last_connection_change).seconds
            last_physical_attempt = (now() - node.last_physical_attempt).seconds
            last_connection_attempt = (now() - node.last_connection_attempt).seconds
            logger.debug("starting state change for %s" % node)
            if node.connection_state_id == 2:
                if node.connection_attemps == 0:
                    if last_connection_change > 5:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                elif node.connection_attemps < 3:
                    if last_connection_attempt > 10:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                else:
                    if last_connection_attempt > 20:
                        node.set_connection_state(3)
            elif node.connection_state_id == 3:
                if node.connection_attemps < 5:
                    if last_connection_attempt > 100:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                else:
                    if last_connection_attempt > 3600:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
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
                    node.ping()
                    node.set_physical_state(1)
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
                    node.set_physical_state(1)
                    node.ping()
            elif node.physical_state_id == 3:
                if node.house.duration <= last_physical_change:
                    node.close_valve()
            logger.debug("finished state change for %s" % node)
            session.commit()
        else:
            logger.debug("not checking %s because it's gateway is not connected" % node)
    logger.debug("done checking nodes")
loop()
