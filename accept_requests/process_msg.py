import pika
import json
import requests
import redis
from utility import consume_message_from_queue, store_status_in_redis, callback, get_redis_connection
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


def process_msg():
    consume_message_from_queue(exchange_name, "process_messaging", "process", cb)


def cb(ch, method, properties, body):
    """
    :param ch: Channel
    :param method:
    :param properties:
    :param body: body of the message
    :return:
    """
    try:
        print(" [x] %r:%r" % (method.routing_key, body))
        payload = json.loads(body)
        msg, callback_url, uid, msg_time  = processing(payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        status = send_message(msg)
        # if message is delivered to the client
        if status == 200:
            msg_status = "delivered"  #sent and delivered
        else:
            msg_status = "sent"       #sent from our side and not sure delivered to the cient
        payload = {"message": msg, "status": msg_status,
                   "callback_url": callback_url, "time": msg_time}
        if redis_entry_exists(uid, payload, 0) == False:
            callback(uid, callback_url, msg, msg_status)


    except Exception as ex:
        print "Error received: " + str(ex)


def processing(payload):
    """
    :param payload:
    :return: msg, payload, uid
    """
    print "msg is " + payload["message"]
    print "url is " + payload["callback_url"]
    print "uid is " + payload["uid"]
    print "msg_time is" + payload["time"]

    return payload["message"], payload["callback_url"], payload["uid"], payload["time"]


def send_message(msg):
    """
    Function to send the message to the client.
    Msg can be sms, email, push notification etc.
    :param msg:
    :return:
    """
    status = send_message_to_client()
    return status


def send_message_to_client(msg):
    """
    method to get the status of the message sent.
    I am assuming that the status of 200 means a successful sent message.
    :return: status
    """
    status = 200
    return status

def redis_entry_exists(uid, payload, db):
    try:
        r = get_redis_connection(db)
        if r.exists(uid):
            r.set(uid, payload)
            return True
        else:
            return False
    except Exception as ex:
        print "error " + str(ex)