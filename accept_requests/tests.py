
import redis
import pika

# Create your tests here.

from django.test import TestCase
from accept_requests.utility import get_redis_connection, get_status_from_redis, get_notification_channel, create_queue
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


class MessagingTestCase(TestCase):

    def redis_is_up(self):
        """
        CHECK REDIS CONNECTION
        :return:
        """
        r = get_redis_connection(0)
        self.assertTrue(isinstance(r, redis.StrictRedis))

    def get_status(self):
        """
        Check if key doesn't exist in Redis
        :return:
    """
        status = get_status_from_redis("FSFSFSD-44255", 0)
        self.assertEqual(status, "Message Already Processed")

    def rabbitmq_connection(self):
        """
        Check Rabbitmq connection
        :return:
        """
        ch = get_notification_channel()
        self.assertTrue(isinstance(ch, pika.adapters.blocking_connection.BlockingChannel))

    def queue_creation(self):
        """
        Check Queue Creation
        :return:
        """
        try:
            ch = get_notification_channel()
            create_queue(ch, exchange_name, "process_messaging", "process")
            self.assertTrue(True)
        except Exception as ex:
            self.assertFalse(False)


