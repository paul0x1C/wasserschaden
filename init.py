## -*- coding: utf-8 -*-

from db import models, wrapper

db_connect = wrapper.db_connect

connection_states = [
    (1, "connected", "#19ff00"),
    (2, "waiting for ping", "#FF00CC"),
    (3, "disconnected", "#FF3300"),
]

physical_states = [
    (1, "closed", "#00FF66"),
    (2, "should open", "#00FFE5"),
    (3, "open", "#61b4e8"),
    (4, "should close", "#a83cea"),
]

@db_connect
def add_states(session):
    for state in connection_states:
         new_state = models.ConnectionState(id = state[0], name = state[1], color = state[2])
         session.add(new_state)
    for state in physical_states:
         new_state = models.PhysicalState(id = state[0], name = state[1], color = state[2])
         session.add(new_state)

@db_connect
def add_settings(session):
    setting = models.Setting(id = 1, state = 0)
    session.add(setting)

add_states()
add_settings()
