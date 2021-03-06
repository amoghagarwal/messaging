import json
import pika
import requests
import logging
import time

from accept_requests.models import FailedMessages
from accept_requests.utility import get_redis_connection, get_status_from_redis, remove_key_from_redis, \
    consume_message_from_queue
from constants import MAX_NUMBER_OF_RETRIES, TIME_INTERVAL_BETWEEN_EACH_RETRY
log = logging.getLogger(__name__)

from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


class Callbacks:

    def __init__(self):
        self.retries = 1

    def fetch_msg_from_queue(self):
        consume_message_from_queue(exchange_name, "retry_callbacks", "callbacks", self.cb)

    def cb(self,ch, method, properties, body):
        """
        :param ch: Channel
        :param method: method for acknowledgement
        :param properties:
        :param body: Body of the message
        :return:
        """
        log.info(" [x] %r:%r" % (method.routing_key, body))
        payload = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        retry_mechanism(payload, self.retries)


def retry(payload, retry_count):
    """
    Utility function for callbacks
    :param payload:
    :param retry_count:
    :return:
    """
    try:
        msg, callback_url, uid = unpack(payload, retry_count)
        status = get_status_from_redis(uid, 0)
        if status != "Message Already Processed":
            body = {"message": msg, "status": status}
            r = requests.post(callback_url, data=body)
            return r.status_code
    except Exception as ex:
        import traceback
        log.error(traceback.format_exc())
        return -1


def retry_mechanism(payload, retry_count):
    """
    Keeps on retrying callback till a max number
    :param payload:
    :param retry_count:
    :return:
    """
    uid = payload["uid"]
    while retry_count <= MAX_NUMBER_OF_RETRIES:
        status_code = retry(payload, retry_count)
        if status_code != 200:
            retry_count += 1
            time.sleep(TIME_INTERVAL_BETWEEN_EACH_RETRY)
        else:
            remove_key_from_redis(uid, 0)
            break
    if retry_count > MAX_NUMBER_OF_RETRIES:
        store_info_in_db(payload, retry_count)
        remove_key_from_redis(uid, 0)
        log.info("Finished retrying callback for the message")

def unpack(payload, retry_count):
    """
    To unserialize the data
    :param payload:

    :return: msg, payload, uid
    """
    log.info("retry count: " + str(retry_count))
    log.info("msg is " + payload["message"])
    log.info("url is " + payload["callback_url"])
    log.info("uid is " + payload["uid"])

    return payload["message"], payload["callback_url"], payload["uid"]


def unpack_without_print(payload, retry_count):
    return payload["message"], payload["callback_url"], payload["uid"]


def store_info_in_db(payload, retry_count):
    """
    Function to store the failed attempts in DB. This is for backup.
    :param payload: The data to be stored in table
    :param retry_count: The number of retries to be stored in table
    :return:
    """
    try:
        msg, url, uid = unpack_without_print(payload, retry_count)
        status = get_status_from_redis(uid, 0)
        FailedMessages.objects.create(uid=uid, callback_url=url, message=msg, status=status, retries=retry_count)
        log.info("Storing Record in DB")
    except Exception as ex:
        log.error("Error while saving info in DB: " + str(ex))
