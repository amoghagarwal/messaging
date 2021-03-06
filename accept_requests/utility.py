import redis
from appsphere import settings
import pika
import requests
import json
import logging
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name

notification_channel = None
log = logging.getLogger(__name__)

def get_redis_connection(db):
    """
    A utility function that will return a redis connection.
    """
    try:
        return redis.StrictRedis(host=settings.SR_REDIS_HOST,
                                 port=settings.SR_REDIS_PORT,
                                 db=db)
    except Exception as ex:
        log.error('Unable to connect to redis. ' + str(ex))


def consume_message_from_queue(exchange_name, queue_name, routing_key, cb):
    """
    Common helper method to register callback to get messages from queue.

    :param exchange_name: Name of the exchange to bind.
    :param queue_name: Name of the queue to be used.

    :param cb: callback method which will get messages. Given below is the signature of cb method.
                        def cb(channel, method, properties, body):
    """
    channel = get_notification_channel()
    create_queue(channel, exchange_name, queue_name, routing_key)
    channel.basic_consume(cb, queue=queue_name)
    channel.start_consuming()


def create_queue(channel, exchange_name, queue_name, routing_key):
    """
    Create a queue for given exchange and queue name (and routing queue).
    :param channel: channel for rabbitMQ
    :param exchange_name: exchange name
    :param queue_name: queue name
    :param routing_key: routing key
    """
    channel.exchange_declare(exchange=exchange_name, type='direct')
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)


def get_notification_channel():
    """
    :return: RabbitMQ Channel for notification.
    To maintain a single connection throughout the code.
    """
    global notification_channel
    if notification_channel is None:
        connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_IP))
        notification_channel = connection.channel()
    return notification_channel


def publish_messages_to_queue(exchange_name, routing_key, queue_name, payload):
    """
    :param exchange_name: Name of the exchange to bind.
    :param routing_key: routing key
    :param queue_name: Name of the queue to be used.
    :param payload: the messaget to be enqueued
    :return:
    """
    channel = get_notification_channel()
    create_queue(channel, exchange_name, queue_name, routing_key)
    channel.basic_publish(exchange=exchange_name,
                          routing_key=routing_key,
                          body=payload,
                          properties=pika.BasicProperties(
                          delivery_mode=2,  # make message persistent
                          )
                          )


def get_callback_status(callback_url, msg, status):
    """
    :param uid: Unique ID of the message
    :param callback_url: the url for the callback
    :param msg: the contents of the message
    :param status: the status of the message to be sent
    :return:
    """
    try:
        payload = {"status": status, "message":msg}
        r = requests.post(callback_url, data=payload)
        return r.status_code
    except Exception as ex:
        log.error("Unable to Send Callbacks: " + str(ex))
        return -1


def store_status_in_redis(uid, status, db):
    """
    :param uid: Unique ID of the message
    :param payload: value to be stored in redis
    :param db: db number to be used in redis
    :return:
    """
    try:
        r = get_redis_connection(db)
        r.set(uid, status)
    except Exception as ex:
        log.error("Unable to store status in redis: " + str(ex))


def callback(uid, callback_url, msg, msg_status):
    """
    :param uid: Unique ID of the message
    :param callback_url: the url for the callback
    :param msg: the url for the callback
    :param msg_status: Status of the message to be communicated
    :return:
    """
    try:
        callback_status = get_callback_status(callback_url, msg, msg_status)
        if callback_status != 200:
            store_status_in_redis(uid, msg_status, 0)
            call_retry_mechanism(msg, uid, callback_url)
    except Exception as ex:
        log.error("Unable to Send Callbacks")
        import traceback
        log.error(traceback.format_exc())


def call_retry_mechanism(msg, uid, callback_url):
    """
    :param msg: the contents of the message
    :param uid: Unique ID of the message
    :param callback_url: the url for the callback
    :return:
    """
    payload = {"message": msg, "uid":uid, "callback_url":callback_url}
    payload_encoded = json.dumps(payload)
    publish_messages_to_queue(exchange_name, "callbacks",
                              "retry_callbacks", payload_encoded)


def get_status_from_redis(uid, db):
    """
    :param uid: uid of the message to be deleted
    :param db: name of the redis db
    :return: status
    """
    try:
        r = get_redis_connection(db)
        if r.exists(uid):
            status = r.get(uid)
            return status
        else:
            return "Message Already Processed"
    except Exception as ex:
        import traceback
        log.error(traceback.format_exc())


def remove_key_from_redis(uid,db):
    """
    :param uid: uid of the message to be deleted
    :param db: name of the redis db
    :return:
    """
    try:
        r = get_redis_connection(db)
        r.delete(uid)
        log.info("Message entry removed from redis")
    except Exception as ex:
        log.error("unable to remove keys:")
        import traceback
        log.error(traceback.format_exc())


def redis_entry_exists(uid, payload, db):
    """
    Function to check if redis entry exists
    :param uid:
    :param payload:
    :param db:
    :return:
    """
    try:
        r = get_redis_connection(db)
        if r.exists(uid) and r.get(uid)=="queued":
            r.set(uid, payload)
            return True
        else:
            return False
    except Exception as ex:
        log.error("error " + str(ex))
