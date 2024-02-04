import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

import nest_asyncio
import psycopg2

from src.settings.logging import logger
from src.settings.settings import app_settings

SUBSCRIPTIONS = {}
ACTIVE_EXECUTORS = {}


class Subscription:
    def __init__(self, channel: str, queue: Queue, is_active_callback):
        self.channel = channel
        self.queue = queue
        self.is_active = is_active_callback

    def unsubscribe(self):
        subscriptions = SUBSCRIPTIONS.get(self.channel)
        if (subscriptions):
            subscriptions.remove(self)
        if (not subscriptions):
            executor = ACTIVE_EXECUTORS.get(self.channel)
            executor.shutdown()
            del ACTIVE_EXECUTORS[self.channel]
            del SUBSCRIPTIONS[self.channel]


class SubscriptionService:

    @staticmethod
    def subscribe(channel: str, queue: Queue, is_active_callback) -> Subscription:
        subscription = Subscription(channel, queue, is_active_callback)
        if (channel in SUBSCRIPTIONS):
            SUBSCRIPTIONS.get(channel, []).append(subscription)
            logger.info(f"Already subscribed to {channel}")
            return subscription
        executor = ThreadPoolExecutor(max_workers=1)
        SUBSCRIPTIONS[channel] = [subscription]
        ACTIVE_EXECUTORS[channel] = executor
        loop = asyncio.get_event_loop()
        loop.run_in_executor(executor, _subscribe, channel)
        return subscription


# Needed to use psycopg directly to be able to poll the events
def _fetch_connection():
    conn = psycopg2.connect(
        host=app_settings.pg_host,
        dbname=app_settings.pg_db_name,
        user=app_settings.pg_user,
        password=app_settings.pg_password
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def _subscribe(channel: str):
    connection = _fetch_connection()
    logger.info(f"Subscribing to {channel}")
    cursor = connection.cursor()
    cursor.execute(f"LISTEN {channel};")
    cursor.close()
    logger.info("Starting async loop")
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    try:
        task = loop.create_task(_loop(connection, channel))
        loop.run_until_complete(task)
        logger.info(f'Subscription for {channel} finished')
    except:
        logger.exception('Exception in subscribe')
    finally:
        connection.close()


async def _loop(connection, channel):
    # while (active_callback()):
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(connection, _handle_notify, connection, channel)
        loop.run_until_complete(_has_subscriptions(channel=channel))
        logger.info('Loop finished')
        return True
    except:
        logger.exception('Loop finished with exception')


def _handle_notify(connection, channel: str):
    try:
        connection.poll()
        for notify in connection.notifies:
            payload = notify.payload
            logger.info(f"Received notification {payload}")
            subscriptions = SUBSCRIPTIONS.get(channel)
            for subscription in subscriptions:
                is_active = subscription.is_active
                if (is_active()):
                    queue = subscription.queue
                    queue.put(payload)
                else:
                    subscriptions.remove(subscription)
        connection.notifies.clear()
    except:
        logger.exception('Exception in handle notify')


async def _has_subscriptions(channel: str):
    try:
        while (SUBSCRIPTIONS.get(channel)):
            await asyncio.sleep(1)

        return False
    except:
        logger.exception('Exception in is completed')
        return False
