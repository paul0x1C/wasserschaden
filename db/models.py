from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from db import wrapper
db_connect = wrapper.db_connect
from . import connection

import datetime, logging, os

def now():
    return datetime.datetime.now()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()



class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    gps = Column(String(50))
    interval = Column(Integer)
    duration = Column(Integer)
    last_flush = Column(DateTime)
    adress = Column(String(100))
    mqtt_topic = Column(String(100))
    gateway_state = Column(Boolean)
    gateway_updated = Column(DateTime)
    locked = Column(Boolean)
    locked_since = Column(DateTime)

    def lock(self):
        self.locked = True
        self.locked_since = now()

    def unlock(self):
        self.locked = False

class Floor(Base):
    __tablename__ = 'floors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey('houses.id'))
    house = relationship("House", foreign_keys=[house_id], backref="floors")
    level = Column(Integer)

class Flat(Base):
    __tablename__ = 'flats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    floor = relationship("Floor", foreign_keys=[floor_id], backref="flats")
    name = Column(String(50))

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(BigInteger, primary_key=True)
    flat_id = Column(Integer, ForeignKey('flats.id'))
    flat = relationship("Flat", foreign_keys=[flat_id], backref="nodes")
    name = Column(String(50))
    connection_state_id = Column(Integer, ForeignKey('connection_states.id'))
    connection_state = relationship("ConnectionState", foreign_keys=[connection_state_id], backref="nodes")
    physical_state_id = Column(Integer, ForeignKey('physical_states.id'))
    physical_state = relationship("PhysicalState", foreign_keys=[physical_state_id], backref="nodes")
    last_physical_change = Column(DateTime)
    last_connection_change = Column(DateTime)
    last_physical_attempt = Column(DateTime)
    last_connection_attempt = Column(DateTime)
    physical_attemps = Column(Integer)
    connection_attemps = Column(Integer)
    reported_offline = Column(Boolean)

    def add_physical_attempt(self, session):
        self.last_physical_attempt = now()
        self.physical_attemps += 1

    def add_connection_attempt(self, session):
        self.last_connection_attempt = now()
        self.connection_attemps += 1

    @db_connect
    def set_physical_state(self, state_id, session, update_time = True):
        self.physical_attemps = 0
        if state_id == 1 and self.physical_state_id == 4:
            house = self.flat.floor.house
            house.unlock()
        self.physical_state_id = state_id
        if update_time:
            self.last_physical_change = now()
        logger.info("Set physical_state of node %s to %s" % (self.id, state_id))
        # print("set", self.id, "state_id")
        report = Report(node_id = self.id, physical_state_id = state_id, time = now())
        session.add(report)

    @db_connect
    def set_connection_state(self, state_id, session, update_time = True):
        if update_time:
            self.last_connection_change = now()
        if state_id == 3 and not self.reported_offline:
            alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' not responding…" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
            session.add(alert)
            self.reported_offline = True
        if state_id == 1 and self.reported_offline:
            self.reported_offline = False
            alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' is back onlin <3" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
            session.add(alert)
        self.connection_attemps = 0
        self.connection_state_id = state_id
        logger.info("Set connection_state of node %s to %s" % (self.id, state_id))

    @db_connect
    def close_valve(self,session):
        self.set_physical_state(4)
        self.send_mqtt_msg("close")
        logger.info("Sending close command to node %s" % self.id)

    @db_connect
    def open_valve(self, session):
        self = session.query(Node).filter(Node.id == self.id).one()
        locked = session.query(House).filter(House.id == self.flat.floor.house.id).one().locked
        if not locked:
            if self.connection_state_id == 1 and self.physical_state_id == 1:
                self.flat.floor.house.lock()
                self.set_physical_state(2)
                self.send_mqtt_msg("open")
                logger.info("Sending open command to node %s" % self.id)
                return True
        return False

    def send_mqtt_msg(self, msg):
        os.system("""mosquitto_pub -t "%s/to/%s" -m "%s" """ % (self.flat.floor.house.mqtt_topic, self.id, msg))

class Report(Base):
    __tablename__ = 'reports'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="reports")
    physical_state_id = Column(Integer, ForeignKey('physical_states.id'))
    physical_state = relationship("PhysicalState", foreign_keys=[physical_state_id], backref="reports")
    time = Column(DateTime)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    priority = Column(Integer)
    added = Column(DateTime)
    sent = Column(DateTime)
    content = Column(String(5000))

class PhysicalState(Base):
    __tablename__ = 'physical_states'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    color = Column(String(8))

class ConnectionState(Base):
    __tablename__ = 'connection_states'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    color = Column(String(8))


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="queue")
    house_id = Column(Integer, ForeignKey('houses.id'))
    house = relationship("House", foreign_keys=[house_id], backref="queue")
    added = Column(DateTime)

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    updated = Column(DateTime)
    status = Column(Integer)
    name = Column(String(50))

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    state = Column(Integer)


Base.metadata.create_all(connection.engine)
