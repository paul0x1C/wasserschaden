# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from key import db_pass

# db_url = 'sqlite:///../db_file/production.db'
db_url = 'mysql://root:%s@172.17.0.2/wasserschaden' % db_pass

engine = create_engine(db_url, echo=False)

Session = sessionmaker(bind=engine)
