# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from key import db_pass

# db_url = 'sqlite:///../db_file/production.db'
db_url = 'mysql://wasser:%s@localhost/wasserschaden?charset=utf8' % db_pass


engine = create_engine(db_url, echo=False)

Session = sessionmaker(bind=engine)
