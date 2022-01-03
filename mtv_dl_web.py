#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import subprocess


class Config:
    # TODO: load config from file
    def __init__(self):
        self.hostName = "localhost"
        self.serverPort = 8080
        self.mtv_dl_binary = "mtv_dl.py"


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # TODO: add "/favicon.ico"
        print(self.path)
        if self.path == "/":
            self.send_file("index.html")
        # elif self.path == "/search.js":
        #     self.send_file("search.js")
        elif self.path == "/search":
            self.mtv_dl_dump()

    def send_file(self, filename):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(open(filename, "rb").read())

    def mtv_dl_dump(self):
        cmd = 'mtv_dl -r 24 dump topic="Nord bei Nordwest"'
        print(f"Starting mtv_dl: {cmd}")
        json = subprocess.check_output(cmd, shell=True)
        print("mtv_dl finished")
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(json)


if __name__ == "__main__":
    config = Config()
    webServer = HTTPServer((config.hostName, config.serverPort), MyServer)
    print("Server started http://%s:%s" % (config.hostName, config.serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
