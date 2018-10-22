# -*- coding: utf-8 -*-
import os, datetime, logging

from db import models, wrapper

db_connect = wrapper.db_connect

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def now():
    return datetime.datetime.now()

def publish_to_node(node, msg):
    os.system("""mosquitto_pub -t "%s/to/%s" -m "%s" """ % (node.flat.floor.house.mqtt_topic, node.id, msg))

class SystemModule():
    @db_connect
    def __init__(self, sys_id, name, session):
        self.id = sys_id
        self.name = name
        if session.query(models.Module).filter(models.Module.id == self.id).count() == 0:
            new_system_module = models.Module(id = sys_id, name = name)
            session.add(new_system_module)
    @db_connect
    def update(self, status, session):
        system_module = session.query(models.Module).filter(models.Module.id == self.id).one()
        system_module.updated = now()
        system_module.status = status

@db_connect
def set_connection_state(node, state_id, session, update_time = True):
    if update_time:
        node.last_connection_change = now()
    if state_id == 3 and not node.reported_offline:
        alert = models.Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' not responding…" % (node.id, node.flat.floor.house.name, node.flat.floor.level, node.flat.name))
        session.add(alert)
        node.reported_offline = True
    if state_id == 1 and node.reported_offline:
        node.reported_offline = False
        alert = models.Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' is back onlin <3" % (node.id, node.flat.floor.house.name, node.flat.floor.level, node.flat.name))
        session.add(alert)
    node.connection_attemps = 0
    node.connection_state_id = state_id
    logger.info("Set connection_state of node %s to %s" % (node.id, state_id))
    # report = models.Report(node_id = node.id, connection_state_id = state_id, physical_state_id = node.physical_state_id, time = now())
    # session.add(report)

@db_connect
def add_physical_attempt(node, session):
    node.last_physical_attempt = now()
    node.physical_attemps += 1

@db_connect
def add_connection_attempt(node, session):
    node.last_connection_attempt = now()
    node.connection_attemps += 1

@db_connect
def set_physical_state(node, state_id, session, update_time = True):
    if update_time:
        node.last_physical_change = now()
    node.physical_attemps = 0
    node.physical_state_id = state_id
    logger.info("Set physical_state of node %s to %s" % (node.id, state_id))
    report = models.Report(node_id = node.id, physical_state_id = state_id, time = now())
    session.add(report)

@db_connect
def set_setting(setting_id, state, session):
    setting = session.query(models.Setting).filter(models.Setting.id == setting_id)
    logger.info("Setting setting %s to %s" % (setting_id, state))
    if setting.count() > 0:
        setting = setting.first()
        setting.state = int(state)
    else:
        new_setting = models.Setting(id = setting_id, state = int(state))
        session.add(new_setting)

@db_connect
def broadcast_ping(gateway_topic, session):
    houses = session.query(models.House).filter(models.House.mqtt_topic == gateway_topic)
    for house in houses:
        for floor in house.floors:
            for flat in floor.flats:
                for node in flat.nodes:
                    set_connection_state(node, 2)
    os.system("""mosquitto_pub -t "%s/to/broadcast" -m ping """ % (gateway_topic))

@db_connect
def close_valve(node_id,session):
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    set_physical_state(node, 4)
    publish_to_node(node, "close")
    logger.info("Sending close command to node %s" % node_id)

@db_connect
def open_valve(node_id,session):
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    nodes = session.query(models.Node)
    open_nodes = 0
    for n in nodes:
        if n.physical_state_id in [2,3,4] and node.flat.floor.house.id ==  n.flat.floor.house.id:
            open_nodes += 1
    if open_nodes == 0:
        if node.connection_state_id == 1 and node.physical_state_id == 1:
            set_physical_state(node, 2)
            publish_to_node(node, "open")
            logger.info("Sending open command to node %s" % node.id)
            return True
    return False
