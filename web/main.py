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

def decorate(decorater, text, args = []):
    arg_string = ""
    for arg in args:
        arg_string += " %s='%s'" % (arg[0], arg[1])
    return "<%s%s>%s</%s>" % (decorater,arg_string,text,decorater)

@app.route('/overview', methods=['GET', 'POST'])
@db_connect
def overview(session):
    content = ""
    # content += str(request.form)
    autorefresh = check_autorefesh(request)
    if request.form.get('action') == "add_house":
        house = models.House(
            name = request.form.get('name'),
            gps = request.form.get('gps'),
            mqtt_topic = request.form.get('mqtt_topic'),
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
    elif request.form.get('action') == "edit_house":
        house = session.query(models.House).filter(models.House.id == int(request.form.get('house_id'))).one()
        house.length = int(request.form.get('length'))
        house.interval = int(request.form.get('interval'))
        house.mqtt_topic = request.form.get('mqtt_topic')
    elif request.form.get('action') == "del_house":
        house = session.query(models.House).filter(models.House.id == int(request.form.get('house_id'))).first()
        content += "removed house"
        for object in delete_house(house):
            session.delete(object)
    elif request.form.get('action') == "del_floor":
        floor = session.query(models.Floor).filter(models.Floor.id == int(request.form.get('floor_id'))).first()
        content += "removed floor"
        delete_floor(floor)
    elif request.form.get('action') == "del_flat":
        flat = session.query(models.Flat).filter(models.Flat.id == int(request.form.get('flat_id'))).first()
        content += "removed flat"
        delete_flat(flat)
    houses = session.query(models.House)
    system_modules = session.query(models.System)
    return content+render_template('overview.html',system_modules=system_modules, autorefresh = autorefresh, base_template = 'base.html', houses = houses, sorted=sorted, attrgetter=attrgetter, node_id=0, int=int)

@app.route('/node_info', methods=['GET', 'POST'])
def node_info():
    return get_node_info(request)

def delete_house(house, to_delete):
    for floor in house.floors:
        to_delete.append(floor)
    to_delete.append(house)
    return to_delete

def delete_floor(floor, to_delete):
    for flat in floor.flats:
        to_delete.append(flat)
    to_delete.append(floor)
    return to_delete

def delete_flat(flat, to_delete):
    for node in flat.nodes:
        to_delete.append(node)
    to_delete.append(flat)
    return to_delete

def delete_node(node, to_delete):
    for report in node.reports:
        to_delete.append(report)
    for que in node.queue:
        to_delete.append(que)
    to_delete.append(node)
    return to_delete

def check_autorefesh(request):
    if request.args.get('autorefresh'):
        return True
    return False

@db_connect
def get_node_info(request, session):
    autorefresh = check_autorefesh(request)
    node_id = int(request.args.get('node_id'))
    if request.form.get('action') == "ping":
        publish_to_node(session.query(models.Node).filter(models.Node.id == node_id).one(), "ping")
        set_state(node_id, 5)
    elif request.form.get('action') == "move":
        node = session.query(models.Node).filter(models.Node.id == node_id).first()
        node.flat_id = int(request.form.get('flat_id'))
    node = session.query(models.Node).filter(models.Node.id == node_id).first()
    houses = session.query(models.House)
    reports = node.reports[-20:]
    reports.reverse()
    return render_template('node_info.html', autorefresh = autorefresh, base_template = 'base.html', node = node, houses = houses, reports = reports, node_id = node.id, int=int)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
