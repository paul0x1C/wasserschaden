## -*- coding: utf-8 -*-

import sys
from flask import Flask, request, render_template, Response, jsonify
from operator import attrgetter
sys.path.append("..")
from db import models
from db import wrapper
from actions import *

db_connect = wrapper.db_connect

app = Flask(__name__)

@app.route('/overview', methods=['GET', 'POST'])
@db_connect
def overview(session):
    content = ""
    # content += str(request.form)
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
    elif request.form.get('action') == "clear_queue":
        queue = session.query(models.Queue)
        for que in queue:
            if que.node.flat.floor.house.id == int(request.form.get('house_id')):
                session.delete(que)
    elif request.form.get('action') == "del_house":
        house = session.query(models.House).filter(models.House.id == int(request.form.get('house_id'))).one()
        content += "removed house"
        delete_house(house, session)
    elif request.form.get('action') == "del_floor":
        floor = session.query(models.Floor).filter(models.Floor.id == int(request.form.get('floor_id'))).one()
        content += "removed floor"
        delete_floor(floor, session)
    elif request.form.get('action') == "del_flat":
        flat = session.query(models.Flat).filter(models.Flat.id == int(request.form.get('flat_id'))).one()
        content += "removed flat"
        delete_flat(flat, session)
    houses = session.query(models.House)
    system_modules = session.query(models.System)
    return content+render_template('overview.html', system_modules=system_modules, base_template = 'base.html', houses = houses, sorted=sorted, attrgetter=attrgetter, node_id=0, int=int, str=str)

@app.route('/node_info', methods=['GET', 'POST'])
@db_connect
def node_info(session):
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
    return render_template('node_info.html', base_template = 'base.html', node = node, houses = houses, reports = reports, node_id = node.id, int=int)

@app.route('/csv', methods=['GET'])
@db_connect
def csv(session):
    house_id = request.args.get('house_id')
    columns = []
    report_query = session.query(models.Report)
    reports = []
    for report in report_query:
        if report.node.flat.floor.house.id == int(house_id):
            reports.append(report)
    nodes = []
    for report in reports:
        if not report.node in nodes:
            nodes.append(report.node)
    column = ["time"]
    for node in nodes:
        column.append("%s: %s-%s" % (node.flat.floor.level, node.flat.name, node.id))
    columns.append(column)
    for report in reports:
        if report.state_id in [3,4]:
            column = [str(report.time)]
            for x in range(nodes.index(report.node)):
                column.append("-")
            if report.state_id == 3:
                column.append("open")
            elif report.state_id == 4:
                column.append("close")
            for x in range(len(nodes) - (nodes.index(report.node)+1)):
                column.append("-")
            columns.append(column)
    csv_string = ""
    for column in columns:
        csv_string += ",".join(column) + "\n"
    return Response(csv_string, mimetype="text/csv")

@app.route('/auto_update')
@db_connect
def auto_update(session): # returns all the self updateing stuff
    nodes = session.query(models.Node)
    houses = session.query(models.House)
    modules = session.query(models.System)
    result = {"html": [], "bgColor": []}
    for node in nodes:
        result['bgColor'].append(("Nco" + str(node.id), node.state.color))
    for house in houses:
        result['html'].append(("Hst" + str(house.id), house.gateway_state))
        result['html'].append(("Hsi" + str(house.id), house.gateway_updated))
        result['html'].append(("Hqu" + str(house.id), queue_length(house)))
    for module in modules:
        result['html'].append(("Mst" + str(module.id), module.status))
        result['html'].append(("Msi" + str(module.id), module.updated))
    return jsonify(result)


def delete_house(house, session):
    for floor in house.floors:
        delete_floor(floor, session)
    session.delete(house)

def delete_floor(floor, session):
    for flat in floor.flats:
        delete_flat(flat, session)
    session.delete(floor)

def delete_flat(flat, session):
    for node in flat.nodes:
        delete_node(node, session)
    session.delete(flat)

def delete_node(node, session):
    for report in node.reports:
        session.delete(report)
    for que in node.queue:
        session.delete(que)
    session.delete(node)

@db_connect
def queue_length(house, session):
    counter = 0
    queue = session.query(models.Queue)
    for que in queue:
        if que.node.flat.floor.house.id == house.id:
            counter += 1
    return counter

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
