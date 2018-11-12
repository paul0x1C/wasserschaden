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

priority_emojis = ["", "ℹ","❓","❗","‼","⁉","🔥"]

def access_conrol(func):
    def inner(*args, **kwargs):
        if args[1].message.chat_id == chat_id:
            return func(*args, **kwargs)
        else:
            args[1].message.reply_text('nope')
            logger.warning("Blocked acces for %s" % args[1].message.from_user)
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
        update.message.reply_text("please provide an Integer")
    else:
        set_setting(1, priority)
        update.message.reply_text("priority set to %i" % priority)

@db_connect
def button(bot, update, session):
    data = update.callback_query.data
    data = data.split('|')
    from_chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    if chat_id == from_chat_id:
        if data[0] == "H":
            house = session.query(models.House).filter(models.House.id == int(data[1])).first()
            keyboard = []
            msg = house.name
            msg += "\nInterval (s): " + str(house.interval)
            msg += "\nDuration (s): " + str(house.duration)
            msg += "\nLast Flush: " + str(house.last_flush)
            msg += "\nAdress: " + str(house.adress)
            msg += "\nNodes: " + str(len(house.nodes))
            msg += "\nfloors:" + str(len(house.floors))
            floors = session.query(models.Floor).filter(models.Floor.house_id == house.id).order_by(models.Floor.level.desc())
            for floor in floors:
                keyboard.append([InlineKeyboardButton("floor %s" % floor.level, callback_data = "F|%s" % floor.id)])
            keyboard.append([InlineKeyboardButton("boradcast ping", callback_data = "Hp|%s" % house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "F":
            floor = session.query(models.Floor).filter(models.Floor.id == int(data[1])).first()
            keyboard = []
            msg = "Floor %s in house '%s'" % (floor.level, floor.house.name)
            msg += "\nflats:"
            for flat in floor.flats:
                keyboard.append([InlineKeyboardButton(flat.name, callback_data = "f|%s" % flat.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "H|%s" % floor.house.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "f":
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
            node = session.query(models.Node).filter(models.Node.id == int(data[1])).one()
            msg = str(node)
            msg += "\n" + node.connection_state.name
            msg += "\n" + node.physical_state.name
            keyboard = []
            keyboard.append([InlineKeyboardButton("reload " + now().strftime("%a %d.%m. %H:%M:%S"), callback_data = "N|%s" % node.id)])
            keyboard.append([InlineKeyboardButton("ping", callback_data = "Np|%s" % node.id)])
            keyboard.append([InlineKeyboardButton("🔙", callback_data = "f|%s" % node.flat.id)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.editMessageText(message_id=message_id, chat_id=chat_id, text=msg, reply_markup=reply_markup)
        elif data[0] == "Np":
            node = session.query(models.Node).filter(models.Node.id == int(data[1])).one()
            node.ping()
            bot.sendMessage(chat_id, "pinged node")
        elif data[0] == "Hp":
            house = session.query(models.House).filter(models.House.id == int(data[1])).one()
            broadcast_ping(house.mqtt_topic)
            bot.sendMessage(chat_id, "broadcasting ping")
        elif data[0] == "u":
            set_new_node_flat(int(data[1]))
            bot.sendMessage(chat_id, "Okay")

@db_connect
def send_alerts(bot, job, session):
    system_module.update(1)
    priority_setting = session.query(models.Setting.state).filter(models.Setting.id == 1).one()
    alerts = session.query(models.Alert).filter(models.Alert.priority >= priority_setting)
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
            session.delete(alert)
        alert_msg = ""
        for entry in to_send:
            if entry[0] > 1:
                alert_msg += "\n({}x) {}".format(entry[0], entry[1])
            else:
                alert_msg += "\n{}".format(entry[1])
        while len(alert_msg) > 3000:
            bot.sendMessage(chat_id, alert_msg[:3000])
            alert_msg = alert_msg[3000:]
        bot.sendMessage(chat_id, alert_msg)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater(api_key) # located in key.py

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list_houses", list_houses))
    dp.add_handler(CommandHandler("set_priority", set_priority))
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
