from . import models
from sqlalchemy import types
from datetime import datetime,timezone


class UTCDateTime(types.TypeDecorator):

    impl = types.BigInteger
    # impl = dialects.mysql.DATETIME

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(timezone.utc).timestamp() * 1000

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime.utcfromtimestamp(value/1000).replace(tzinfo=timezone.utc).astimezone()

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
    inner.__name__ = "db_" + func.__name__
    return inner
