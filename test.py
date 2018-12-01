from actions import *

@db_connect
def test(session):
    node = session.query(models.Node).first()
    print(node.average_response_time())

test()
