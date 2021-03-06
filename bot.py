## -*- coding: utf-8 -*-
from telegram import *
from telegram.ext import *

from key import api_key, chat_id
from db import models, wrapper
from actions import *

import logging

db_connect = wrapper.db_connect

system_module = SystemModule(3, "telegram_bot")
system_module.update(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

priority_emojis = ["", "ℹ","❔","❓","⚠️","❌","🔥","☄️","💥","📉"]

def access_conrol(func):
    def inner(*args, **kwargs):
        if args[1].message == None:
            a_chat_id = args[1].callback_query.message.chat_id
            from_user = args[1].callback_query.message.from_user
        else:
            a_chat_id = args[1].message.chat_id
            from_user = args[1].message.from_user
        if a_chat_id == chat_id:
            return func(*args, **kwargs)
        else:
            log("Blocked acces for {}".format(from_user), 3, 0)
    return inner

@access_conrol
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('yes, it still works…')

@db_connect
@access_conrol
def msg(bot, update, session):
    print(update.message)

@db_connect
@access_conrol
def list_houses(bot, update, session):
    houses = session.query(models.House)
    keyboard = []
    msg = "Houses"
    for house in houses:
        keyboard.append([InlineKeyboardButton(house.name, callback_data = "H|%s" % house.id)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(msg, reply_markup=reply_markup)

@access_conrol
def set_priority(bot, update):
    last_char = update.message.text[-1:]
    try:
        priority = int(last_char)
    except:
        keyboard = []
        for priority in range(1,10):
            keyboard.append([InlineKeyboardButton("{} {}".format(priority, priority_emojis[priority]), callback_data = "p|%s" % priority)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(chat_id=chat_id, text="select priority", reply_markup=reply_markup)
    else:
        set_setting(1, priority)
        update.message.reply_text("priority set to %i" % priority)

@db_connect
@access_conrol
def status(bot, update, session):
    msg_text, reply_markup = gen_status_msg()
    update.message.reply_text(msg_text, reply_markup=reply_markup)

@db_connect
@access_conrol
def clean_alerts(bot, update, session):
    priority_setting = session.query(models.Setting).filter(models.Setting.id == 1).one().state
    alerts = session.query(models.Alert).filter((models.Alert.priority < priority_setting) & (models.Alert.sent == None))
    counter = 0
    for alert in alerts:
        alert.sent = now()
        counter += 1
    update.message.reply_text("set {} alerts to sent".format(counter))

@db_connect
def gen_status_msg(session):
    msg = []
    keyboard = []
    for house in session.query(models.House):
        keyboard.append([InlineKeyboardButton("ping {}".format(house), callback_data = "Hp|%s" % house.id)])
        msg.append(house)
        msg.append([])
        for floor in house.floors:
            msg[-1].append(floor)
            msg[-1].append([])
            for flat in floor.flats:
                msg[-1][-1].append(flat)
                msg[-1][-1].append([])
                for node in flat.nodes:
                    msg[-1][-1][-1].append(node.connection_state.emoji + node.physical_state.emoji + str(node.id))
                    if node.has_sense_plate:
                        if node.sense:
                            msg[-1][-1][-1][-1] += "🚨"
                        else:
                            msg[-1][-1][-1][-1] += "💹"
                    msg[-1][-1][-1][-1] += " rtt~" + str(int(node.average_response_time()*1000)) + "ms"
    keyboard.append([InlineKeyboardButton("reload " + now().strftime("%a %d.%m. %H:%M:%S"), callback_data = "S")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return unfold_msg_list(msg), reply_markup

def unfold_msg_list(stack, spacing = 0):
    msg = ""
    for part in stack:
        if isinstance(part, list):
            msg += unfold_msg_list(part, spacing+3)
        else:
            msg += "\n" + " "*spacing + str(part)
    return msg

@db_connect
@access_conrol
def button(bot, update, session):
    data = update.callback_query.data
    data = data.split('|')
    from_chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    if chat_id == from_chat_id:
        if data[0] == "H": # house info
            house = session.query(models.House).filter(models.House.id == int(data[1])).first()
            keyboard = []
            msg = house.name
            msg += """\nInterval (s): {}\nDuration (s): {}\nLast Flush: {}\nAdress: {}\nNodes: {}\nfloors: {}
            """.format(house.interval, house.duration, house.last_flush, house.adress, len(house.nodes), len(house.floors))
            floors = session.query(models.Floor).filter(models.Floor.house_id == house.id).order_by(models.Floor.level.desc())
            for floor in floors:
                keyboard.append([InlineKeyboardButton("floor %s" % floor.level, callback_data = "F|%s" % floor.id)])
            keyboard.append([InlineKeyboardButton("boradcast ping", callback_data = "Hp|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("flush now", callback_data = "Hf|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("clear queue", callback_data = "Hc|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("show queue", callback_data = "Hq|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("node stats", callback_data = "Hs|%s" % house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "F": # floor info
            floor = session.query(models.Floor).filter(models.Floor.id == int(data[1])).first()
            keyboard = []
            msg = "Floor %s in house '%s'" % (floor.level, floor.house.name)
            msg += "\nflats:"
            for flat in floor.flats:
                keyboard.append([InlineKeyboardButton(flat.name, callback_data = "f|%s" % flat.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "H|%s" % floor.house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "f": # flat info
            flat = session.query(models.Flat).filter(models.Flat.id == int(data[1])).first()
            keyboard = []
            msg = "Flat '%s' on floor %s in house '%s'" % (flat.name, flat.floor.level, flat.floor.house.name)
            msg += "\nnodes:"
            keyboard.append([InlineKeyboardButton("use for new nodes", callback_data="u|%s" % flat.id)])
            for node in flat.nodes:
                keyboard.append([InlineKeyboardButton("node %s" % node.id, callback_data = "N|%s" % node.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "F|%s" % flat.floor.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "N":
            msg, reply_markup = node_info_msg(int(data[1]))
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "Np": # ping node
            node = session.query(models.Node).filter(models.Node.id == int(data[1])).one()
            node.ping()
            bot.sendMessage(chat_id, "pinged node")
        elif data[0] == "Nq": # queue node
            node = session.query(models.Node).filter(models.Node.id == int(data[1])).one()
            que = models.Queue(node_id = node.id, house_id = node.house.id, added = now())
            session.add(que)
            bot.sendMessage(chat_id, "queued {}".format(node))
        elif data[0] == "Ns": # set has_sense_plate for node
            node = session.query(models.Node).filter(models.Node.id == int(data[1])).one()
            node.has_sense_plate = bool(int(data[2]))
            session.commit()
            msg, reply_markup = node_info_msg(int(data[1]))
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "Hp": # ping whole house
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            broadcast_ping(house.mqtt_topic)
            bot.sendMessage(chat_id, "broadcasting ping")
        elif data[0] == "Hc": # clear que
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            queue = session.query(models.Queue)
            counter = 0
            for que in queue:
                if que.node.flat.floor.house.id == house.id:
                    session.delete(que)
                    counter += 1
            bot.sendMessage(chat_id, "deleted {} entries from {}'s queue".format(counter, house))
        elif data[0] == "Hq": # show house que
            keyboard = []
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            queue = session.query(models.Queue)
            msg = "Queue of {}".format(house)
            for que in queue:
                if que.node.flat.floor.house.id == house.id:
                    msg += "\n{}{}{}".format(que.node.connection_state.emoji, que.node.physical_state.emoji,que.node.id)
            keyboard.append([InlineKeyboardButton("clear queue", callback_data = "Hc|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("refresh", callback_data = "Hq|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "H|%s" % house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "Hf": # initiate flush for house
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            house.init_flush()
            bot.sendMessage(chat_id, "initiated flush for {}".format(house))
        elif data[0] == "Hs": # return node stats
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            states = {}
            keyboard =[]
            msg = house.name
            for node in house.nodes:
                if not node.physical_state.name in states:
                    states[node.physical_state.name] = 0
                states[node.physical_state.name] += 1
                if not node.connection_state.name in states:
                    states[node.connection_state.name] = 0
                states[node.connection_state.name] += 1
            for state, n in states.items():
                msg += "\n{}: {}".format(state,n)
            keyboard.append([InlineKeyboardButton("boradcast ping", callback_data = "Hp|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("refresh", callback_data = "Hs|%s" % house.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "H|%s" % house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "u": # set flat for new nodes
            set_new_node_flat(int(data[1]))
            bot.sendMessage(chat_id, "Okay")
        elif data[0] == "p": # set priority
            set_setting(1, int(data[1]))
            msg = "alert priority set to {}".format(data[1])
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg)
        elif data[0] == "S": # resend status msg
            msg, reply_markup = gen_status_msg()
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)

@db_connect
def node_info_msg(node_id, session):
    node = session.query(models.Node).filter(models.Node.id == node_id).one()
    msg = str(node)
    msg += "\n" + node.connection_state.name
    msg += "\n" + node.physical_state.name
    msg += "\nhas temp sensor: {}".format(node.has_temperature_sensor)
    msg += "\nhas water sensor: {}".format(node.has_sense_plate)
    keyboard = []
    keyboard.append([InlineKeyboardButton("reload " + now().strftime("%a %d.%m. %H:%M:%S"), callback_data = "N|%s" % node.id)])
    keyboard.append([InlineKeyboardButton("ping", callback_data = "Np|%s" % node.id)])
    keyboard.append([InlineKeyboardButton("add to queue", callback_data = "Nq|%s" % node.id)])
    if node.has_sense_plate:
        keyboard.append([InlineKeyboardButton("no sense plate", callback_data = "Ns|%s|0" % node.id)])
    else:
        keyboard.append([InlineKeyboardButton("has sense plate", callback_data = "Ns|%s|1" % node.id)])
    keyboard.append([InlineKeyboardButton("🔙", callback_data = "f|%s" % node.flat.id)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return msg, reply_markup

@db_connect
@access_conrol
def module_status():
    pass

@db_connect
def send_alerts(bot, job, session):
    system_module.update(1)
    priority_setting = session.query(models.Setting).filter(models.Setting.id == 1).one().state
    alerts = session.query(models.Alert).filter((models.Alert.priority >= priority_setting) & (models.Alert.sent == None))
    if alerts.count() > 0:
        to_send = []
        for alert in alerts:
            msg = "{} {}".format(priority_emojis[alert.priority], alert.content)
            if to_send:
                if to_send[-1][1] == msg:
                    to_send[-1][0] += 1
                else:
                    to_send.append([1, msg])
            else:
                to_send.append([1, msg]) # this repitition is pretty ugly :(
            alert.sent = now()
        alert_msg = ""
        for entry in to_send:
            if entry[0] > 1:
                alert_msg += "\n({}x) {}".format(entry[0], entry[1])
            else:
                alert_msg += "\n{}".format(entry[1])
        if len(to_send) == 1: # only do this when sending a single msg
            text = to_send[0][1]
            keyboard = []
            try:
                for i in text.split('<')[1:]:
                    representer = i.split('>')[0] # try to find representers
                    if "id=" in representer:
                        object_id = representer.split("id=")[1].split(",")[0] # extract the id
                        if representer[:5] == "House":
                            house = session.query(models.House).filter(models.House.id == object_id).one()
                            keyboard.append([InlineKeyboardButton(representer, callback_data = "H|%s" % house.id)])
                        elif representer[:4] == "Flat":
                            flat = session.query(models.Flat).filter(models.Flat.id == object_id).one()
                            keyboard.append([InlineKeyboardButton(representer, callback_data = "F|%s" % flat.id)])
                        elif representer[:4] == "Node":
                            node = session.query(models.Node).filter(models.Node.id == object_id).one()
                            keyboard.append([InlineKeyboardButton(representer, callback_data = "N|%s" % node.id)])
            except:
                log("alert reply buttons produced an exception", 3)
            bot.sendMessage(chat_id, text, reply_markup=InlineKeyboardMarkup(keyboard))

        else:
            send(bot, alert_msg)

def send(bot, text):
    while len(text) > 3000:
        bot.sendMessage(chat_id, text[:3000])
        text = text[3000:]
    bot.sendMessage(chat_id, text)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    log('Update "{}" caused error "{}"'.format(update, error), 3, 0)

def main():
    updater = Updater(api_key) # located in key.py

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list_houses", list_houses))
    dp.add_handler(CommandHandler("set_priority", set_priority))
    dp.add_handler(CommandHandler("clean_alerts", clean_alerts))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(MessageHandler(Filters.text, msg))

    j = updater.job_queue
    j.run_repeating(send_alerts,1.0,1.0)
    j.start()

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
