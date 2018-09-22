from db import models, wrapper

db_connect = wrapper.db_connect

states = [
    (1, "idle", "#19ff00"),
    (2, "should open", "#00fff6"),
    (3, "open", "#61b4e8"),
    (4, "should close", "#a83cea"),
    (5, "waiting for ping", "#ff004c"),
    (6, "open and disconnected", "#ff0000"),
    (9, "disconnected", "#bc0000"),
    (21, "should open - retry 1", "#dcf464"),
    (22, "should open - retry 2", "#f4c464"),
    (41, "should close - retry 1", "#ea3cdf"),
    (42, "should close - retry 2", "#ea3ca5")
]

@db_connect
def add_states(session):
    for state in states:
        #s = session.query(models.State).filter(models.State.id == state[0]).one()
        #s.color = state[2]
         new_state = models.State(id = state[0], name = state[1], color = state[2])
         session.add(new_state)

add_states()
