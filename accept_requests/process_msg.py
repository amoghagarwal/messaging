import json
import requests
import logging
import time
from utility import consume_message_from_queue, store_status_in_redis, callback, get_redis_connection, \
    redis_entry_exists
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name

log = logging.getLogger(__name__)

def process_msg():
    """
    Function to consume messages from the queue, process them and then send them
    :return:
    """
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
        log.info(" [x] %r:%r" % (method.routing_key, body))
        payload = json.loads(body)
        msg, callback_url, uid = processing(payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        status = send_message(msg)
        # if message is delivered to the client
        if status == 200:
            msg_status = "delivered"  #sent and delivered
        else:
            msg_status = "sent"       #sent from our side and not sure delivered to the cient
        payload = {"message": msg, "status": msg_status,
                   "callback_url": callback_url}
        if not redis_entry_exists(uid, payload, 0):
            callback(uid, callback_url, msg, msg_status)


    except Exception as ex:
        log.error("Error received: " + str(ex))


def processing(payload):
    """
    :param payload:
    :return: msg, payload, uid
    """
    print "msg is " + payload["message"]
    print "url is " + payload["callback_url"]
    print "uid is " + payload["uid"]

    return payload["message"], payload["callback_url"], payload["uid"]


def send_message(msg):
    """
    Function to send the message to the client.
    Msg can be sms, email, push notification etc.
    :param msg:
    :return:
    """
    status = send_message_to_client(msg)
    return status


def send_message_to_client(msg):
    """
    method to get the status of the message sent.
    I am assuming that the status of 200 means a successful sent message.
    :return: status
    """
    time.sleep(2) #sending a request and getting response will take time
    status = 200
    return status


