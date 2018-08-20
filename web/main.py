## -*- coding: utf-8 -*-

import sys
from flask import Flask, request, render_template
from operator import attrgetter
sys.path.append("..")
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect


app = Flask(__name__)

utf8 = """<meta charset="utf-8">"""


def decorate(decorater, text, args = []):
    arg_string = ""
    for arg in args:
        arg_string += " %s='%s'" % (arg[0], arg[1])
    return "<%s%s>%s</%s>" % (decorater,arg_string,text,decorater)

@app.route('/overview', methods=['GET', 'POST'])
@db_connect
def overview(session):
    content = utf8
    # content += str(request.form)
    if request.form.get('action') == "add_house":
        house = models.House(
            name = request.form.get('name'),
            gps = request.form.get('gps'),
            adress = request.form.get('adress'),
            interval = int(request.form.get('interval')),
            length = int(request.form.get('length'))
        )
        content += "added house"
        session.add(house)
    elif request.form.get('action') == "add_floor":
        floor = models.Floor(level = int(request.form.get('level')),
            house_id = int(request.form.get('house_id')))
        content += "added floor"
        session.add(floor)
    elif request.form.get('action') == "add_flat":
        flat = models.Flat(name = request.form.get('name'),
            floor_id = int(request.form.get('floor_id')))
        content += "added flat"
        session.add(flat)
    elif request.form.get('action') == "del_floor":
        floor = session.query(models.Floor).filter(models.Floor.id == int(request.form.get('floor_id'))).first()
        content += "removed floor"
        session.delete(floor)
    elif request.form.get('action') == "del_flat":
        flat = session.query(models.Flat).filter(models.Flat.id == int(request.form.get('flat_id'))).first()
        content += "removed flat"
        session.delete(flat)
    houses = session.query(models.House)
    return content+render_template('overview.html', houses = houses, sorted=sorted, attrgetter=attrgetter)

@app.route('/node_info', methods=['GET', 'POST'])
def node_info():
    if request.form.get('action') == "ping":
        node_id = int(request.form.get('node_id'))
        publish_to_node(node_id, "ping")
        set_state(node_id, 5)
    return get_node_info(request.args.get('node_id'))

@db_connect
def get_node_info(node_id, session):
    node = session.query(models.Node).filter(models.Node.id == node_id).first()
    return render_template('node_info.html', node = node)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
