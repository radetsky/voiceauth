import logging
import os
import psycopg2
from asterisk.ami import AMIClient


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


def db_connect():
    logging.info('Connecting to the database')
    dbname = os.getenv('DB_NAME')
    dbhost = os.getenv('DB_HOST')
    dbuser = os.getenv('DB_USER')
    dbpass = os.getenv('DB_PASS')

    conn = psycopg2.connect(
        f"dbname={dbname} user={dbuser} password={dbpass} host={dbhost}")

    return conn


def ami_connect():
    logging.info('Connecting to the asterisk manager interface')
    ami_host = os.getenv('AMI_HOST')
    ami_port = int(os.getenv('AMI_PORT'))
    ami_user = os.getenv('AMI_USER')
    ami_pass = os.getenv('AMI_PASS')

    client = AMIClient(address=ami_host, port=ami_port)
    client.login(username=ami_user, secret=ami_pass)
    return client


if __name__ == "__main__":
    # Connect to your postgres DB
    conn = db_connect()
    ami = ami_connect()
