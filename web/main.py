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
    content = "" # used for status messages
    if request.form.get('action') == "add_house":
        house = models.House(
            name = request.form.get('name'),
            gps = request.form.get('gps'),
            mqtt_topic = request.form.get('mqtt_topic'),
            adress = request.form.get('adress'),
            interval = int(request.form.get('interval')),
            duration = int(request.form.get('duration')),
            locked = False,
            locked_since = now(),
            bridge_last_attempt = now(),
            bridge_state = 0
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
        house.duration = int(request.form.get('duration'))
        house.interval = int(request.form.get('interval'))
        house.mqtt_topic = request.form.get('mqtt_topic')
    elif request.form.get('action') == "clear_queue":
        queue = session.query(models.Queue)
        for que in queue:
            if que.node.flat.floor.house.id == int(request.form.get('house_id')):
                session.delete(que)
    elif request.form.get('action') == "broadcast_ping":
        content += "broadcast_ping"
        broadcast_ping(request.form.get('bridge_topic'))
    elif request.form.get('action') == "reset_temp_sensor_status":
        content += "reset temperature sensor status"
        house_id = int(request.form.get('house_id'))
        house = session.query(models.House).filter(models.House.id == house_id).one()
        house.reset_temp_sensor_status()
    elif request.form.get('action') == "flush_now":
        content += "flush now"
        house_id = int(request.form.get('house_id'))
        house = session.query(models.House).filter(models.House.id == house_id).one()
        house.init_flush()
    elif request.form.get('action') == "set_setting":
        set_setting(int(request.form.get('setting')), int(request.form.get('value')))
    elif request.form.get('action') == "set_new_node_flat":
        set_new_node_flat(int(request.form.get('flat_id')))
    houses = session.query(models.House)
    system_modules = session.query(models.Module)
    n_nodes = session.query(models.Node).count() # number of nodes, so the js can check wether new nodes connected
    return content+render_template('overview.html',
                                    system_modules=system_modules,
                                    base_template = 'base.html',
                                    houses = houses, sorted=sorted,
                                    attrgetter=attrgetter, node_id=0,
                                    int=int, str=str,
                                    n_nodes=n_nodes
                                )

@app.route('/node_info', methods=['GET', 'POST'])
@db_connect
def node_info(session):
    node_id = int(request.args.get('node_id'))
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    if request.form.get('action') == "ping":
        node.ping()
    elif request.form.get('action') == "move":
        node = session.query(models.Node).filter(models.Node.id == node_id).first()
        node.flat_id = int(request.form.get('flat_id'))
        node.house_id = node.flat.floor.house.id
    node = session.query(models.Node).filter(models.Node.id == node_id).first()
    houses = session.query(models.House)
    reports = node.reports[-30:] # only show 30 newest reports
    reports.reverse()
    return render_template('node_info.html',
                            base_template = 'base.html',
                            node = node,
                            houses = houses,
                            reports = reports,
                            node_id = node.id,
                            int=int
                        )

@app.route('/csv', methods=['GET'])
@db_connect
def csv(session): # generates csv for display in excel
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
        if report.physical_state_id in [3,4]:
            column = [str(report.time)]
            for x in range(nodes.index(report.node)):
                column.append("-")
            if report.physical_state_id == 3:
                column.append("open")
            elif report.physical_state_id == 4:
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
def auto_update(session): # returns all the self updateing stuff, is called every second by js
    nodes = session.query(models.Node)
    houses = session.query(models.House)
    modules = session.query(models.Module)
    result = {"html": [], "bgColor": [], "boColor": [], "refresh": False}
    if not int(request.args.get('n_nodes')) == nodes.count():
        result['refresh'] = True
    for node in nodes:
        result['bgColor'].append(("Nco" + str(node.id), node.physical_state.color))
        result['boColor'].append(("Nco" + str(node.id), node.connection_state.color))
        if node.has_sense_plate:
            result['html'].append(("Nhs" + str(node.id), "💧"))
            if node.sense:
                result['html'].append(("Nds" + str(node.id), "🚨"))
            else:
                result['html'].append(("Nds" + str(node.id), "💹"))
    for house in houses:
        result['html'].append(("Hst" + str(house.id), house.bridge_state))
        result['html'].append(("Hsi" + str(house.id), house.bridge_updated.strftime("%a %d.%m. %H:%M:%S")))
        result['html'].append(("Hqu" + str(house.id), queue_length(house)))
        result['html'].append(("Hlk" + str(house.id), house.locked))
        if house.interval > 0 and house.last_flush:
            result['html'].append(("Hnf" + str(house.id), (datetime.timedelta(seconds = house.interval) + house.last_flush).strftime("%a %d.%m. %H:%M:%S")))
        else:
            result['html'].append(("Hnf" + str(house.id), "None"))
    for module in modules:
        result['html'].append(("Mst" + str(module.id), module.status))
        result['html'].append(("Msi" + str(module.id), module.updated.strftime("%a %d.%m. %H:%M:%S")))
    return jsonify(result)

@app.route('/delete', methods=['POST','GET'])
@db_connect
def delete(session):
    content = ""
    if request.form.get('action') == "del_house":
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
    elif request.form.get('action') == "del_node":
        node = session.query(models.Node).filter(models.Node.id == int(request.form.get('node_id'))).one()
        content += "removed node"
        delete_node(node, session)
    houses = session.query(models.House)
    return content + render_template('delete.html',
                                    base_template = 'base.html',
                                    houses = houses, sorted=sorted,
                                    attrgetter=attrgetter,
                                    int=int, str=str
                                )


def delete_house(house, session):
    house.new_node_flat = None
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
    for temperature in node.temperatures:
        session.delete(temperature)
    session.delete(node)

@db_connect
def queue_length(house, session): # returns que length for a house
    counter = 0
    queue = session.query(models.Queue)
    for que in queue:
        if que.house_id == house.id:
            counter += 1
    return counter

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
