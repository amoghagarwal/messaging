from django.test import TestCase
import redis
import pika

# Create your tests here.
from accept_requests.utility import get_redis_connection, get_status_from_redis, get_notification_channel


class RedisTestCase(TestCase):

    def setUp(self):
        pass

    def redis_is_up(self):
        """
        CHECK REDIS CONNECTION
        :return:
        """
        r = get_redis_connection(0)
        return self.assertTrue(isinstance(r, redis.StrictRedis))

    def get_status(self):
        """
        Check if key doesn't exist in Redis
        :return:
        """
        status = get_status_from_redis("FSFSFSD-44255", 0)
        return self.assertEqual(status, "Message Already Processed")

    def queue_connection(self):
        """
        Check Rabbitmq connection
        :return:
        """
        ch = get_notification_channel()
        return self.assertTrue(isinstance(ch, pika.adapters.blocking_connection.BlockingChannel))


