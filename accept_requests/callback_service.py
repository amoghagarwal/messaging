import json
import pika
import requests
import redis
import time

from accept_requests.utility import get_redis_connection, get_status_from_redis, remove_key_from_redis, \
    consume_message_from_queue
from constants import MAX_NUMBER_OF_RETRIES, TIME_INTERVAL_BETWEEN_EACH_RETRY

from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


class Callbacks:

    def __init__(self):
        self.retries = 1

    def fetch_msg_from_queue(self):
        consume_message_from_queue(exchange_name, "retry_callbacks", "callbacks", self.cb)

    def cb(self,ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        payload = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        retry(payload, self.retries)


def retry(payload, retry_count):
    if retry_count > MAX_NUMBER_OF_RETRIES:
        return
    msg, callback_url, uid = unpack(payload)
    status = get_status_from_redis(uid, 0)
    if status != "Message Already Processed":
        body = {"message": msg, "status": status}
        r = requests.post(callback_url, data=body)
        if r.status_code != 200:
            retry_count += 1
            time.sleep(TIME_INTERVAL_BETWEEN_EACH_RETRY)
            retry(payload, retry_count)
        else:
            remove_key_from_redis()
            return


def unpack(payload):
    """
    :param payload:
    :return: msg, payload, uid
    """
    print "msg is " + payload["message"]
    print "url is " + payload["callback_url"]
    print "uid is " + payload["uid"]

    return payload["message"], payload["callback_url"], payload["uid"]


