import logging
import os
import psycopg2
import argparse
import random
from asterisk.ami import AMIClient, SimpleAction


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


def db_connect():
    logging.debug('Connecting to the database')
    dbname = os.getenv('DB_NAME')
    dbhost = os.getenv('DB_HOST')
    dbuser = os.getenv('DB_USER')
    dbpass = os.getenv('DB_PASS')

    conn = psycopg2.connect(
        f"dbname={dbname} user={dbuser} password={dbpass} host={dbhost}")

    return conn


def ami_connect():
    logging.debug('Connecting to the asterisk manager interface')
    ami_host = os.getenv('AMI_HOST')
    ami_port = int(os.getenv('AMI_PORT'))
    ami_user = os.getenv('AMI_USER')
    ami_pass = os.getenv('AMI_PASS')

    client = AMIClient(address=ami_host, port=ami_port)
    client.login(username=ami_user, secret=ami_pass)
    return client


def read_callerids():
    with open('callerids.txt', 'r') as file:
        data = file.read().rstrip().split('\n')

    logging.debug(data)
    return data


def print_status():
    logging.info("Database is connected")
    logging.info("Asterisk is connected")
    logging.info(f"CallerIDs: {len(callerids)}")
    logging.info(f"Processes: 1")


def select_first_available():
    cursor = conn.cursor()
    db_table = os.getenv('DB_TABLE')
    cursor.execute(
        f"SELECT dst from {db_table} where updated is null order by created limit 1 for update")
    number = cursor.fetchone()[0]
    return number


def get_callerid():
    return random.choice(callerids)


def call_dst(dst: str):
    logging.info(f"Calling to {dst}")
    channel = os.getenv('AMI_CHANNEL')
    context = os.getenv('AMI_CONTEXT')
    callerid = get_callerid()
    action = SimpleAction(
        'Originate',
        Channel=channel,
        Exten=dst,
        Priority=1,
        Context=context,
        CallerID=callerid,
    )
    logging.info(action)
    future = ami.send_action(action)
    response = future.response
    logging.info(response)
    print(response.response)


def process():
    '''
        Select first available number to call 
        Call 
        Wait for the answer
        Webhook 
    '''
    dst = select_first_available()
    call_dst(dst)


if __name__ == "__main__":
    # Connect to your postgres DB
    conn = db_connect()
    ami = ami_connect()
    callerids = read_callerids()
    print_status()
    process()
