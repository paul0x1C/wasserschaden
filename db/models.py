from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from db.wrapper import *
from . import connection
from actions import log, logger, now, broadcast_ping

import datetime, os

Base = declarative_base()



class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    gps = Column(String(50))
    interval = Column(Integer)
    duration = Column(Integer)
    last_flush = Column(UTCDateTime, default = now())
    adress = Column(String(100))
    mqtt_topic = Column(String(100))
    gateway_state = Column(Integer)
    gateway_updated = Column(UTCDateTime, default = now())
    gateway_last_attempt = Column(UTCDateTime, default = now())
    new_node_flat_id = Column(Integer, ForeignKey('flats.id'))
    new_node_flat = relationship("Flat", foreign_keys=[new_node_flat_id], backref="new_node_houses")
    locked = Column(Boolean)
    locked_since = Column(UTCDateTime, default = now())

    def lock(self):
        self.locked = True
        self.locked_since = now()

    def unlock(self):
        self.locked = False

    @db_connect
    def init_flush(self, session):
        log("Initiating new flush for {}".format(self), 2, 1)
        broadcast_ping(self.mqtt_topic)
        for node in self.nodes:
            if session.query(Queue).filter(Queue.node_id == node.id).count() == 0: #check whether node is already queued
                que = Queue(node_id = node.id, house_id = self.id, added = now())
                session.add(que)
            else:
                log("Tried to add a node to {}'s queue, but it was already in the queue".format(self), 3, 2)
        self.last_flush = now()

    def reset_temp_sensor_status(self):
        log("Reseting temperature sensor status", 2)
        for node in self.nodes:
            node.has_temperature_sensor = True

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
    last_physical_change = Column(UTCDateTime, default = now())
    last_connection_change = Column(UTCDateTime, default = now())
    last_physical_attempt = Column(UTCDateTime, default = now())
    last_connection_attempt = Column(UTCDateTime, default = now())
    physical_attempts = Column(Integer) # counts the attempts that were made to close/open the valve
    connection_attempts = Column(Integer) # counts the ping attempts
    sense = Column(Boolean) # True if the node detects water
    sense_update = Column(UTCDateTime, default = now())
    has_sense_pin = Column(Boolean)
    last_temperature_update = Column(UTCDateTime, default = now())
    has_temperature_sensor = Column(Boolean)
    last_temeparture_request = Column(UTCDateTime, default = now())
    reported_offline = Column(Boolean)


    def add_physical_attempt(self):
        self.last_physical_attempt = now()
        self.physical_attempts += 1

    def add_connection_attempt(self):
        self.last_connection_attempt = now()
        self.connection_attempts += 1

    @db_connect
    def add_temperature(self, value, session):
        if not value == -127.0: # -127.0 is sent, when there is no sensor
            entry = Temperature(
                node_id = self.id,
                value = value,
                time = now()
            )
            self.has_temperature_sensor = True
            session.add(entry)
            session.commit()
            log("stored temperature {} for {}".format(value, self), 1)
        elif self.has_temperature_sensor:
            self.has_temperature_sensor = False
            session.commit()
            log("{} sent temperature -127°C but should have a had sensor".format(self), 3, 2)
        self.last_temperature_update = now()

    @db_connect
    def set_physical_state(self, state_id, session, update_time = True):
        self.physical_attempts = 0
        self.physical_state_id = state_id
        if update_time:
            self.last_physical_change = now()
        log("Set physical_state of node {} to {}".format(self, state_id), 2)
        report = Report(node_id = self.id, physical_state_id = state_id, time = now())
        session.add(report)

    # @db_connect
    def set_connection_state(self, state_id, update_time = True):
        if update_time and self.connection_state_id is not state_id:
            if not (self.connection_state_id in [2,3] and state_id in [2,3]):
                self.last_connection_change = now()
        # if state_id == 3 and not self.reported_offline:
        #     alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' not responding…" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
        #     session.add(alert)
        #     self.reported_offline = True
        # if state_id == 1 and self.reported_offline:
        #     self.reported_offline = False
        #     alert = Alert(added = now(), content="Node %s in House '%s' on floor %s in flat '%s' is back onlin <3" % (self.id, self.flat.floor.house.name, self.flat.floor.level, self.flat.name))
        #     session.add(alert)
        self.connection_attempts = 0
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
        return False # return False when there was no 'open' command sent

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

class Report(Base): # logs physical_states of nodes
    __tablename__ = 'reports'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="reports")
    physical_state_id = Column(Integer, ForeignKey('physical_states.id'))
    physical_state = relationship("PhysicalState", foreign_keys=[physical_state_id], backref="reports")
    time = Column(UTCDateTime, default = now())

class Alert(Base): # messages to be sent to telegram group
    __tablename__ = 'alerts'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    priority = Column(Integer)
    added = Column(UTCDateTime, default = now())
    sent = Column(UTCDateTime, default = None)
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
    added = Column(UTCDateTime, default = now())

class Temperature(Base):
    __tablename__ = 'temperatures'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(BigInteger, ForeignKey('nodes.id'))
    node = relationship("Node", foreign_keys=[node_id], backref="temperatures")
    time = Column(UTCDateTime, default = now())
    value = Column(Float)

class Module(Base): # logs state of running python scripts
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    updated = Column(UTCDateTime, default = now())
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
