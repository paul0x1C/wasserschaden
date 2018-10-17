## -*- coding: utf-8 -*-

import sys
from flask import Flask, request, render_template, Response
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
    return content+render_template('overview.html',system_modules=system_modules, autorefresh = autorefresh, base_template = 'base.html', houses = houses, sorted=sorted, attrgetter=attrgetter, node_id=0, int=int, queue_length=queue_length)

@app.route('/node_info', methods=['GET', 'POST'])
def node_info():
    return get_node_info(request)

@app.route('/csv', methods=['GET'])
def csv():
    csv = get_csv(request.args.get('house_id'))
    return Response(csv, mimetype="text/csv")

@db_connect
def get_csv(house_id, session):
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
        if report.state_id in [1,3]:
            column = [str(report.time)]
            for x in range(nodes.index(report.node)):
                column.append("-")
            if report.state_id == 1:
                column.append("open")
            elif report.state_id == 3:
                column.append("close")
            for x in range(len(nodes) - (nodes.index(report.node)+1)):
                column.append("-")
            columns.append(column)
    csv_string = ""
    for column in columns:
        csv_string += ",".join(column) + "\n"
    return csv_string
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
