# -*- coding: utf-8 -*-
import os, datetime, logging

from db import models, wrapper

db_connect = wrapper.db_connect

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def now():
    return datetime.datetime.now().astimezone()

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
        module = session.query(models.Module).filter(models.Module.id == self.id).one()
        module.updated = now()
        module.status = status

def log(text, logger_level = 0, alert_priority = 0):
    if logger_level == 1:
        logger.debug(text)
    elif logger_level == 2:
        logger.info(text)
    elif logger_level == 3:
        logger.warning(text)
    elif logger_level == 4:
        logger.error(text)
    if alert_priority:
        add_alert(text, alert_priority)

@db_connect
def add_alert(alert_text, priority, session):
    alert = models.Alert(content = alert_text, added = now(), priority = priority)
    session.add(alert)

@db_connect
def set_new_node_flat(flat_id, session):
    flat = session.query(models.Flat).filter(models.Flat.id == flat_id).one()
    house = flat.floor.house
    house.new_node_flat = flat
    log("Using flat {} ('{}') for new nodes in house {} ('{}')".format(flat.id, flat.name, house.id, house.name), 2, 0)

@db_connect
def set_setting(setting_id, state, session):
    setting = session.query(models.Setting).filter(models.Setting.id == setting_id)
    log("Setting setting {} to {}".format(setting_id, state), 2, 0)
    if setting.count() > 0:
        setting = setting.first()
        setting.state = int(state)
    else:
        new_setting = models.Setting(id = setting_id, state = int(state))
        session.add(new_setting)

@db_connect
def broadcast_ping(gateway_topic, session):
    house = session.query(models.House).filter(models.House.mqtt_topic == gateway_topic).one()
    for node in house.nodes:
        node.set_connection_state(2)
    send_mqtt_msg("{}/to/broadcast".format(gateway_topic), "ping")

def send_mqtt_msg(topic, payload):
    os.system("""mosquitto_pub -t "{}" -m "{}" """.format(topic, payload))
