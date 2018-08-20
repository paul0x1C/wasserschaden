from . import models

def db_connect(func):
    def inner(*args, **kwargs):
        session = models.connection.Session()
        return_value = False
        try:
            return_value = func(*args, session=session, **kwargs)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return return_value
    return inner
