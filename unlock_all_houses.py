from db import wrapper

db_connect = rapper.db_connect

@db_connect
def unlock_them_all(session):
    houses = session.query(models.House)
    for house in houses:
        house.unlock()

unlock_them_all()
