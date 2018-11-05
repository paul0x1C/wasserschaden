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
            check_nodes()
            process_queue()
            check_houses()
        except:
            e = traceback.format_exc()
            logger.error(e)
            # add_alert(e)

@db_connect
def add_alert(alert_text, session):
    alert_text += "exception in timer_loop:\n"
    alert = models.Alert(content = alert_text, added = now())
    session.add(alert)

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
        if house.last_flush == None: # make sure last_flush is set
            house.last_flush = datetime.datetime(1,1,1)

        if (now() - house.last_flush).seconds > house.interval and not house.interval == 0: # check if house needs to be flushed
            logger.info("Initiating new flush for house %s" % house)
            for node in house.nodes:
                que = models.Queue(node_id = node.id, house_id = house.id, added = now())
                session.add(que)
            house.last_flush = now()

        if house.locked and (now() - house.locked_since).seconds > 200: # check if house is locked for a too long time
            house.unlock()
            logger.warning("Lock for house %s timed out!" % house)

    logger.debug("done checking houses")

@db_connect
def check_nodes(session):
    nodes = session.query(models.Node).filter((models.Node.physical_state_id > 1) | (models.Node.connection_state_id > 1))
    logger.debug("checking node timeouts")
    for node in nodes:
        node.state_change()
        session.commit()
    logger.debug("done checking nodes")
loop()
