# -*- coding: utf-8 -*

import logging, datetime
from . import models

logger = logging.getLogger(__name__)

def db_connect(func):
    def inner(*args, **kwargs):
        session = models.connection.Session()
        try:
            func(*args, session=session, **kwargs)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    return inner

@db_connect
def add_house(name,gps,session):
    house = models.House(name = name, gps = gps)
    session.add(house)
    logger.info("Added house %s" % house)
    return house

@db_connect
def add_floor(house_id,level):
    floor = models.Floor(house_id = house_id, level = level)
    session.add(floor)
    logger.info("Added floor %s" % floor)
    return floor

@db_connect
def add_flat(name,floor_id,session):
    flat = models.Flat(name = name, floor_id = floor_id)
    session.add(flat)
    logger.info("Added flat %s" % flat)
    return flat

@db_connect
def add_node(name,flat_id,session):
    node = models.Node(name = name, flat_id = flat_id)
    session.add(node)
    logger.info("Added node %s" % node)
    return node

@db_connect
def add_report(content,node_id,session):
    report = models.Report(content = content, node_id = node_id)
    session.add(report)
    logger.info("Added report %s" % report)
    return report
