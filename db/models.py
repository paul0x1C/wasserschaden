from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from . import connection

Base = declarative_base()

class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    gps = Column(String(50))
    interval = Column(Integer)
    length = Column(Integer)
    last_flush = Column(DateTime)
    adress = Column(String(100))
    mqtt_topic = Column(String(100))
    gateway_state = Column(Boolean)
    gateway_updated = Column(DateTime)

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
    content = Column(String(200))

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
