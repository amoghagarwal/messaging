from django.http import HttpResponse
from django.http import HttpResponseBadRequest
import datetime
import uuid
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from accept_requests.utility import get_redis_connection, \
    publish_messages_to_queue, get_callback_status, store_status_in_redis, callback
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name

# Get an instance of a logger
log = logging.getLogger(__name__)

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

    if not callback_url or not msg:
        log.error("%s %s error : Please enter valid message and callback" % (callback_url,msg))
        response = {"error" : "Please enter valid message and callback"}
        return HttpResponseBadRequest(json.dumps(response), content_type='application/json')

    msg_status = "unqueued"
    store_status_in_redis(uid, msg_status, 0)

    if enqueue(msg, uid, callback_url):
        msg_status = "queued"
        callback(uid, callback_url, msg, msg_status)
    else:
        msg_status = "unqueued"
        store_in_redis(callback_url, msg, msg_status, time_received, uid)
    response = {"uid": uid, "message":msg, "status": "request_accepted",
                "time": time_received}
    return HttpResponse(json.dumps(response))


def store_in_redis(callback_url, msg, msg_status, time_received, uid):
    payload = {"message": msg, "status": msg_status,
               "callback_url": callback_url, "time": time_received}
    store_status_in_redis(uid, payload, 1)
    log.error("problem while enqueuing. msg stored in redis Db1")

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
        import traceback
        log.info("Problem while enqueuing message:")
        log.info(traceback.format_exc())
        return False


def landing_service(request):
    """
    API to test the landing page
    :param request:
    :return:
    """
    return HttpResponse("Welcome to messaging app")


@csrf_exempt
def test_api_success(request):
    """
    API for testing callback success
    :param request:
    :return:
    """
    if request.method == 'POST':
        msg = str(request.POST.get('msg', None))
        callback_url = str(request.POST.get('url', None))
    return HttpResponse()


@csrf_exempt
def test_api_failure(request):
    """
    API for testing the callback failure
    :param request:
    :return:
    """
    if request.method == 'POST':
        msg = str(request.POST.get('msg', None))
        callback_url = str(request.POST.get('url', None))
    return HttpResponseBadRequest()