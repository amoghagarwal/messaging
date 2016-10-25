
import redis
import pika

# Create your tests here.

from django.test import TestCase
from accept_requests.utility import get_redis_connection, get_status_from_redis, get_notification_channel, create_queue, \
    remove_key_from_redis
from appsphere.settings import RABBITMQ_EXCHANGE as exchange_name


class RedisTestCase(TestCase):
    def test_redis_is_up(self):
        """
        CHECK REDIS CONNECTION
        :return:
        """
        r = get_redis_connection(0)
        self.assertTrue(isinstance(r, redis.StrictRedis))

    def test_key_exists_in_redis(self):
        """
        Check if key doesn't exist in Redis
        :return:
    """
        status = get_status_from_redis("FSFSFSD-44255", 0)
        self.assertEqual(status, "Message Already Processed")

    def test_remove_key_from_redis(self):
        """
        Check key deletion from Redis
        :return:
        """
        r = get_redis_connection(0)
        r.set("a","b")
        remove_key_from_redis("a", 0)
        if r.exists("a"):
            self.assertFalse(True)
        else:
            self.assertTrue(True)


class RabbitmqTestCase(TestCase):
    def test_rabbitmq_connection(self):
        """
        Check Rabbitmq connection
        :return:
        """
        ch = get_notification_channel()
        self.assertTrue(isinstance(ch, pika.adapters.blocking_connection.BlockingChannel))

    def test_queue_creation(self):
        """
        Check Queue Creation
        :return:
        """
        ch = get_notification_channel()
        create_queue(ch, exchange_name, "process_messaging", "process")
        self.assertTrue(True)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)