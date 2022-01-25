#!/usr/bin/env python
"""
Very simple HTTP server in python (Updated for Python 3.7)

Usage:

    ./dummy-web-server.py -h
    ./dummy-web-server.py -l localhost -p 8000

Send a GET request:

    curl http://localhost:8000

Send a HEAD request:

    curl -I http://localhost:8000

Send a POST request:

    curl -d "foo=bar&bin=baz" http://localhost:8000 -H "X-Auth-Token: testtesttest!"

This code is available for use under the MIT license.

----

Copyright 2021 Brad Montgomery

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    

"""
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import os
import psycopg2


class S(BaseHTTPRequestHandler):
    def _set_headers(self, http_status=200):
        self.send_response(http_status)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def _text(self, message):
        return message.encode("utf-8")

    def auth(self):
        """Return X-Auth-Token header or None"""
        token = self.headers['X-Auth-Token']
        env_token = os.getenv('AUTH_TOKEN')
        if env_token is None:
            # debug. trust'em all.
            logging.error("DEBUG MODE! TRUST'EM ALL. BE CAREFULL!")
            return True
        else:
            if token != env_token:
                logging.error(f"Authentication failed. Token is: {token}")
                return False

        return True

    def _add(self, post_data, remote_addr):
        db_table = os.getenv('DB_TABLE')
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"INSERT INTO {db_table} (dst, remote_addr) VALUES (%s, %s)", (post_data, remote_addr))

        except psycopg2.errors.StringDataRightTruncation:
            self._set_headers(422)
            self.wfile.write(self._text("Unprocessable"))
            conn.rollback()
            return False

        conn.commit()
        cursor.close()
        return True

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._text("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        remote_addr = self.client_address[0]  # TODO: check IP for allowed list
        if not self.auth():
            self._set_headers(401)
            self.wfile.write(self._text("Unauthorized"))
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if not self._add(post_data, remote_addr):
            return

        self._set_headers()
        self.wfile.write(self._text("OK"))


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    try:
        httpd.serve_forever()

    except KeyboardInterrupt:
        pass


def db_connect():
    dbname = os.getenv('DB_NAME')
    dbhost = os.getenv('DB_HOST')
    dbuser = os.getenv('DB_USER')
    dbpass = os.getenv('DB_PASS')
    conn = psycopg2.connect(
        f"dbname={dbname} user={dbuser} password={dbpass} host={dbhost}")

    return conn


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()

    # Connect to your postgres DB
    conn = db_connect()

    run(addr=args.listen, port=args.port)
