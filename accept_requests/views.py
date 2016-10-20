from django.http import HttpResponse
from django.shortcuts import render
import pika
import datetime
import uuid
import requests
import json
import redis
from django.views.decorators.csrf import csrf_exempt

from accept_requests.utility import get_redis_connection, \
    publish_messages_to_queue, get_callback_status, store_status_in_redis, callback
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


@csrf_exempt
def msg_service(request):
    """
    :param request:
    :return:
    """
    msg = None
    callback_url = None
    if request.method == 'POST':
        msg = str(request.POST.get('msg', None))
        callback_url = str(request.POST.get('url', None))

    time_received = str(datetime.datetime.now())
    uid = str(uuid.uuid4())

    if enqueue(msg, uid, callback_url):
        msg_status = "queued"
        callback(uid, callback_url, msg, msg_status)
    else:
        msg_status = "unqueued"
        payload = {"message": msg, "status": msg_status,
                   "callback_url": callback_url, "time": time_received}
        store_status_in_redis(uid, payload, 1)
        print "problem while enqueuing. msg stored in redis Db1"
    response = {"uid": uid, "message":msg, "status": "request_accepted",
                "time": time_received}
    return HttpResponse(json.dumps(response))


def extract_callback_url(request):
    pass


def enqueue(msg, uid, callback_url):
    """
    :param msg:
    :param uid:
    :param callback_url:
    :return:
    """
    try:
        payload = {"message": msg, "uid": uid, "callback_url": callback_url}
        payload_encoded = json.dumps(payload)
        publish_messages_to_queue(exchange_name, "process",
                                  "process_messaging", payload_encoded)
        return True
    except Exception as ex:
        print "Problem while enqueuing message: " + str(ex)
        return False

