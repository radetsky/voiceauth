import logging
import os
from time import sleep
import psycopg2
import random
import json
import requests
from asterisk.ami import AMIClient, SimpleAction
from datetime import datetime, timezone


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


def on_disconnect():
    ami = ami_connect()


def event_listener(event, **kwargs):
    logging.debug(event)

    if event.name == 'DialEnd' and (event.keys["DestChannelStateDesc"] == 'Down' or event.keys["DestChannelStateDesc"] == 'Up'):
        status = event.keys["DialStatus"]
        src = event.keys["DestCallerIDNum"]
        dst = event.keys["DestExten"]
        if src in callerids:
            logging.info(f"--> {src} + {dst} = {status}")


def ami_connect():
    logging.debug('Connecting to the asterisk manager interface')
    ami_host = os.getenv('AMI_HOST')
    ami_port = int(os.getenv('AMI_PORT'))
    ami_user = os.getenv('AMI_USER')
    ami_pass = os.getenv('AMI_PASS')

    client = AMIClient(address=ami_host, port=ami_port, timeout=3600)
    client.login(username=ami_user, secret=ami_pass)
    client.add_event_listener(on_event=event_listener,
                              on_disconnect=on_disconnect,
                              white_list=[
                                  'DialBegin', 'DialState', 'DialEnd'])
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
    logging.info(f"Processes: {ps}")


def select_first_available():
    cursor = conn.cursor()
    db_table = os.getenv('DB_TABLE')
    cursor.execute(
        f"SELECT id, dst from {db_table} where updated is null order by created limit 1 for update skip locked")
    number = cursor.fetchone()
    if number is None:
        raise ValueError

    return number


def get_callerid():
    return random.choice(callerids)


def _update(id: int, dst: str, status: str, callerid: str):
    dt = datetime.now(timezone.utc)
    cursor = conn.cursor()
    db_table = os.getenv('DB_TABLE')
    cursor.execute(
        f"update {db_table} set updated=%s, src=%s, dial_status=%s where dst=%s and id=%s", (dt, callerid, status, dst, id))
    conn.commit()


def _webhook(id: int, dst: str, dial_status: str, callerid: str):
    uri = os.getenv('WEBHOOK')
    payload = {'dst': dst, 'callerid': callerid, 'status': dial_status}
    logging.info(f"POST {uri} {payload}")
    try:
        r = requests.post(uri, data=json.dumps(payload))
        logging.info(r)
    except requests.exceptions.RequestException as e:
        logging.error(e)


def call_dst(id: int, dst: str):
    logging.info(f"Calling to {dst}")
    channel = os.getenv('AMI_CHANNEL')
    context = os.getenv('AMI_CONTEXT')
    callerid = get_callerid()
    action = SimpleAction(
        'Originate',
        ActionID=dst,
        Variable=f"ORIGCID=\"{callerid}\"",
        Channel=f"Local/{dst}@{channel}",
        Exten=dst,
        Priority=1,
        Context=context,
        CallerID=callerid,
        Timeout=60000,
    )
    logging.debug(action)
    resp = ami.send_action(action)
    logging.info(resp.response)
    if resp.response.status == 'Success':
        _update(id, dst, 'ANSWER', callerid)
        _webhook(id, dst, 'ANSWER', callerid)
    if resp.response.status == 'Error':
        _update(id, dst, 'BUSY', callerid)
        _webhook(id, dst, 'BUSY', callerid)


def process():
    '''
        Select first available number to call
        Call
        Wait for the answer
        Webhook
    '''

    try:
        (id, dst) = select_first_available()
        call_dst(id, dst)

    except ValueError:
        logging.info("No destinations to call")

    finally:
        sleep(1)


def setup_processes(count: int):
    logging.info(f"Setup dedicated processes: {count}")
    i = 0
    while i < count:
        pid = os.fork()
        if pid > 0:
            i = i + 1
            continue
        else:
            break


if __name__ == "__main__":

    ps = int(os.getenv("VA_PROCESS_COUNT"))
    if ps is not None and ps > 1:
        setup_processes(ps-1)  # We also use parent process

    # Connect to your postgres DB
    conn = db_connect()
    ami = ami_connect()
    callerids = read_callerids()

    print_status()
    while True:
        try:
            process()

        except (KeyboardInterrupt, SystemExit):
            ami.logoff()
            exit(0)
