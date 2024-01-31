import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

import nest_asyncio
import psycopg2
from src.settings.logging import logger
from src.settings.settings import app_settings


# dbname should be the same for the notifying process

def fetch_connection():
    conn = psycopg2.connect(
        host=app_settings.pg_host,
        dbname=app_settings.pg_db_name,
        user=app_settings.pg_user,
        password=app_settings.pg_password
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def subscribe(channel: str, queue: Queue, executor: ThreadPoolExecutor, is_active_callback):
    loop = asyncio.get_event_loop()
    task = loop.run_in_executor(executor, _subscribe, channel, queue, is_active_callback)
    return task


def _subscribe(channel: str, queue: Queue, is_active_callback):
    connection = fetch_connection()
    logger.info(f"Subscribing to {channel}")
    cursor = connection.cursor()
    cursor.execute(f"LISTEN {channel};")
    cursor.close()
    logger.info("Starting async loop")
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    try:
        task = loop.create_task(_loop(connection, queue, is_active_callback))
        loop.run_until_complete(task)
        logger.info(f'Subscription for {channel} finished')
    except:
        logger.exception('Exception in subscribe')
    finally:
        connection.close()


async def _loop(connection, queue: Queue, active_callback):
    # while (active_callback()):
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(connection, _handle_notify, connection, queue)
        loop.run_until_complete(_is_completed(active_callback))
        logger.info('Loop finished')
        return True
    except:
        logger.exception('Loop finished with exception')


def _handle_notify(connection, queue: Queue):
    try:
        connection.poll()
        for notify in connection.notifies:
            payload = notify.payload
            logger.info(f"Received notification {payload}")
            queue.put(payload)
        connection.notifies.clear()
    except:
        logger.exception('Exception in handle notify')


async def _is_completed(active_callback):
    try:
        while (active_callback()):
            await asyncio.sleep(1)

        return False
    except:
        logger.exception('Exception in is completed')
        return False
