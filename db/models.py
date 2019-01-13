from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from db import wrapper
db_connect = wrapper.db_connect
from . import connection
from actions import log, logger

import datetime, os

def now():
    return datetime.datetime.now()

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
    gateway_state = Column(Integer)
    gateway_updated = Column(DateTime)
    gateway_last_attempt = Column(DateTime)
    new_node_flat_id = Column(Integer, ForeignKey('flats.id'))
    new_node_flat = relationship("Flat", foreign_keys=[new_node_flat_id], backref="new_node_houses")
    locked = Column(Boolean)
    locked_since = Column(DateTime)

    # @db_connect
    def lock(self):
        # house = session.query(House).filter(House.id == self.id).one()
        self.locked = True
        self.locked_since = now()

    # @db_connect
    def unlock(self):
        self.locked = False

    def __repr__(self):
        return "<House id=%i, name='%s'>" % (self.id, self.name)

class Floor(Base):
    __tablename__ = 'floors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey('houses.id'))
    house = relationship("House", foreign_keys=[house_id], backref="floors")
    level = Column(Integer)

    def __repr__(self):
        return "<Floor id=%i, level=%i>" % (self.id, self.level)

class Flat(Base):
    __tablename__ = 'flats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    floor = relationship("Floor", foreign_keys=[floor_id], backref="flats")
    name = Column(String(50))

    def __repr__(self):
        return "<Flat id=%i, name='%s'>" % (self.id, self.name)

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(BigInteger, primary_key=True)
    flat_id = Column(Integer, ForeignKey('flats.id'))
    flat = relationship("Flat", foreign_keys=[flat_id], backref="nodes")
    house_id = Column(Integer, ForeignKey('houses.id'))
    house = relationship("House", foreign_keys=[house_id], backref="nodes")
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
    sense = Column(Boolean)
    sense_update = Column(DateTime)
    has_sense_pin = Column(Boolean)
    last_temperature_update = Column(DateTime)
    has_temperature_sensor = Column(Boolean)
    reported_offline = Column(Boolean)


    def add_physical_attempt(self):
        self.last_physical_attempt = now()
        self.physical_attemps += 1

    def add_connection_attempt(self):
        self.last_connection_attempt = now()
        self.connection_attemps += 1

    @db_connect
    def add_temperature(self, value, session):
        if value == -127.0:
            self.has_temperature_sensor = False
        else:
            self.has_temperature_sensor = True
            entry = Temperature(
                node = self,
                value = value,
                time = now()
            )
            session.add(entry)
        self.last_temperature_update = now()

    @db_connect
    def set_physical_state(self, state_id, session, update_time = True):
        self.physical_attemps = 0
        self.physical_state_id = state_id
        if update_time:
            self.last_physical_change = now()
        log("Set physical_state of node {} to {}".format(self, state_id), 2)
        report = Report(node_id = self.id, physical_state_id = state_id, time = now())
        session.add(report)

    # @db_connect
    def set_connection_state(self, state_id, update_time = True):
        if update_time:
            self.last_connection_change = now()
        # if state_id == 3 and not self.reported_offline:
        #     alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' not responding…" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
        #     session.add(alert)
        #     self.reported_offline = True
        # if state_id == 1 and self.reported_offline:
        #     self.reported_offline = False
        #     alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' is back onlin <3" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
        #     session.add(alert)
        self.connection_attemps = 0
        self.connection_state_id = state_id
        log("Set connection_state of {} to {}".format(self, state_id), 2)

    def close_valve(self):
        self.set_physical_state(4)
        self.send_mqtt_msg("close")
        logger.info("Sending close command to node %s" % self)

    @db_connect
    def open_valve(self, session):
        house = session.query(House).filter(House.id == self.house_id).one()
        if not house.locked:
            if self.connection_state_id == 1 and self.physical_state_id == 1:
                house.lock()
                self.set_physical_state(2)
                self.send_mqtt_msg("open")
                session.commit()
                logger.info("Sending open command to node %s" % self)
                return True
        return False

    def send_mqtt_msg(self, msg):
        os.system("""mosquitto_pub -t "%s/to/%s" -m "%s" """ % (self.house.mqtt_topic, self.id, msg))

    def ping(self, set_connection_state = True):
        if set_connection_state:
            self.set_connection_state(2)
        self.send_mqtt_msg("ping")

    @db_connect
    def average_response_time(self, session):
        reports = session.query(Report).filter(Report.node_id == self.id).order_by(Report.id.desc()).limit(100)
        response_times = []
        last_report = None
        for report in reports:
            if last_report == None:
                last_report = report
            elif report.physical_state_id == 2:
                if last_report.physical_state_id == 3:
                    response_times.append((last_report.time - report.time).total_seconds())
            elif last_report.physical_state_id == 3:
                if report.physical_state_id == 4:
                    response_times.append((last_report.time - report.time).total_seconds())
            last_report = report
        return sum(response_times)/len(response_times)

    def __repr__(self):
        return "<Node id=%i>" % (self.id)

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
    content = Column(Text(50000))

class PhysicalState(Base):
    __tablename__ = 'physical_states'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    color = Column(String(8))
    def __repr__(self):
        return "<PhysicalState id=%i, name='%s'>" % (self.id, self.name)

class ConnectionState(Base):
    __tablename__ = 'connection_states'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    color = Column(String(8))
    def __repr__(self):
        return "<ConnectionState id=%i, name='%s'>" % (self.id, self.name)

class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="queue")
    house_id = Column(Integer, ForeignKey('houses.id'))
    house = relationship("House", foreign_keys=[house_id], backref="queue")
    added = Column(DateTime)

class Temperature(Base):
    __tablename__ = 'temperatures'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="temperatures")
    time = Column(DateTime)
    value = Column(Float)

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
    def __repr__(self):
        return "<Setting id=%i, name='%s'>" % (self.id, self.name)

Base.metadata.create_all(connection.engine)
