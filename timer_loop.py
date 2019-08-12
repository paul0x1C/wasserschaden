## -*- coding: utf-8 -*-

import time, datetime, pdb, random, sys, traceback
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

system_module = SystemModule(1, "timer_loop")

logger.info("Starting timer_loop")

def loop():
    while True:
        time.sleep(1)
        try:
            system_module.update(1)
            check_nodes()
            process_queue()
            check_houses()
            poll_temperatures()
        except:
            e = traceback.format_exc()
            logger.error(e)
            add_alert("Exception in timer loop!", 5)

@db_connect
def poll_temperatures(session):
    nodes = session.query(models.Node).filter(models.Node.has_temperature_sensor)
    interval = session.query(models.Setting).filter(models.Setting.id == 2).one().state
    for node in nodes:
        if (now() - node.last_temeparture_request).seconds >= 10:
            if (now() - node.last_temperature_update).seconds >= interval:
                node.last_temeparture_request = now()
                logger.debug("sending temp poll to {}".format(node))
                node.send_mqtt_msg("temp")

@db_connect
def process_queue(session):
    log("checking que", 1, 0)
    houses = session.query(models.House)
    for house in houses:
        log("checking {}".format(house), 1, 0)
        if house.gateway_state == 1 and not house.locked:
            for q in house.queue:
                if q.node.open_valve():
                    session.delete(q)
                    break;
                else:
                    log("couldn't open {}".format(q.node), 1, 0)
    log("done checking que", 1, 0)

@db_connect
def check_houses(session):
    log("checking houses", 1, 0)
    houses = session.query(models.House)
    for house in houses:
        log("checking {}".format(house), 1, 0)

        if (now() - house.last_flush).seconds > house.interval and not house.interval == 0: # check if house needs to be flushed
            house.init_flush()

        if house.locked and (now() - house.locked_since).seconds > 150: # check if house is locked for a too long time
            if session.query(models.Node).filter((models.Node.physical_state_id > 1)).count() == 0:
                house.unlock()
                log("Lock for house {} timed out!".format(house), 3, 2)
        if not house.gateway_updated:
            house.gateway_updated = datetime.datetime(1,1,1)
        last_gateway_change = (now() - house.gateway_updated).seconds
        """
        gateway_state meanings:
        1: online (-> send pings when last message is older then 60s every 60s)
        2: offline since >90s (-> send ping every 100s)
        3: offline since >1h (-> send ping every 140s)
        """
        if last_gateway_change > 60: # ping gateway if it has not send anything for longer than 60s
            if (now() - house.gateway_last_attempt).seconds > (20 + (40 * (house.gateway_state))): # send ping less often, depening on how long the node is disconnected
                send_mqtt_msg(house.mqtt_topic + "/to/gateway", "ping")
                house.gateway_last_attempt = now()
            if house.gateway_state == 1:
                if last_gateway_change > 90: # set gateway to disconnected when it's not responding for >90s
                    house.gateway_state = 2
                    log("gateway in {} is not responding, setting all its nodes to offline".format(house), 1, 1)
                    for node in house.nodes:
                        node.set_connection_state(3)
            else:
                if last_gateway_change > 3600 and house.gateway_state == 2: # higher priority alert after 1h
                    house.gateway_state = 3
                    log("gateway in {} is not responding since an hour".format(house), 3, 3)



    log("done checking houses", 1, 0)

@db_connect
def check_nodes(session):
    """
    check all nodes that are not in the default states
    """
    nodes = session.query(models.Node).filter((models.Node.physical_state_id > 1) | (models.Node.connection_state_id > 1))
    log("checking node timeouts", 1, 0)
    for node in nodes:
        if node.house.gateway_state == 1:
            last_physical_change = (now() - node.last_physical_change).seconds
            last_connection_change = (now() - node.last_connection_change).seconds
            last_physical_attempt = (now() - node.last_physical_attempt).seconds
            last_connection_attempt = (now() - node.last_connection_attempt).seconds
            log("starting state change for {}".format(node), 1, 0)
            if node.connection_state_id == 2:
                if node.connection_attempts == 0:
                    if last_connection_change > 5:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                elif node.connection_attempts < 3:
                    if last_connection_attempt > 10:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                else:
                    if last_connection_attempt > 20:
                        node.set_connection_state(3)
            elif node.connection_state_id == 3:
                if node.connection_attempts < 5:
                    if last_connection_attempt > 100:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
                else:
                    if last_connection_attempt > 3600:
                        node.send_mqtt_msg("ping")
                        node.add_connection_attempt()
            if node.physical_state_id == 2:
                if node.physical_attempts == 0:
                    if last_physical_change > 5:
                        node.send_mqtt_msg("open")
                        node.add_physical_attempt()
                elif node.physical_attempts < 3:
                    if last_physical_attempt > 10:
                        node.send_mqtt_msg("open")
                        node.add_physical_attempt()
                elif node.physical_attempts == 3:
                    node.ping()
                    node.add_physical_attempt()
                if node.connection_state_id == 1:
                    if last_physical_attempt > 20:
                        node.send_mqtt_msg("open")
                        node.add_physical_attempt()
            elif node.physical_state_id == 4:
                if node.physical_attempts == 0:
                    if last_physical_change > 5:
                        node.send_mqtt_msg("close")
                        node.add_physical_attempt()
                elif node.physical_attempts < 3:
                    if last_physical_attempt > 10:
                        node.send_mqtt_msg("close")
                        node.add_physical_attempt()
                elif node.physical_attempts == 3:
                    node.ping()
                    node.add_physical_attempt()
                if node.connection_state_id == 1:
                    if last_physical_attempt > 20:
                        node.send_mqtt_msg("close")
                        node.add_physical_attempt()
            elif node.physical_state_id == 3:
                if node.house.duration <= last_physical_change:
                    node.close_valve()
            log("finished state change for {}".format(node), 1, 0)
            session.commit()
        else:
            log("not checking {} because it's gateway is not connected".format(node))
    log("done checking nodes", 1, 0)
loop()
