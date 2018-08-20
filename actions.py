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
    os.system("""mosquitto_pub -t "painlessMesh/to/%s" -m "%s" """ % (node, msg))

@db_connect
def set_state(node_id, state_id, session, update_time = True):
    node = session.query(models.Node).filter(models.Node.id == node_id).first()
    if update_time:
        node.last_change = now()
    node.state_id = state_id
    logger.info("Set state of node %s to %s" % (node_id, state_id))
    report = models.Report(node_id = node.id, state_id = state_id, time = now())
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
def close_valve(node_id,session):
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    set_state(node_id, 4)
    publish_to_node(node.id, "close")
    logger.info("Sending close command to node %s" % node_id)

@db_connect
def open_valve(node_id,session):
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    nodes = session.query(models.Node)
    open_nodes = 0
    for n in nodes:
        if n.state_id in [2,21,22,3] and node.flat.floor.house.id ==  n.flat.floor.house.id:
            open_nodes += 1
    if open_nodes == 0 and node.state_id == 1:
        set_state(node_id, 2)
        publish_to_node(node.id, "open")
        logger.info("Sending open command to node %s" % node_id)
        return True
    else:
        return False
