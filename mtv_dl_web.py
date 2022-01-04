#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import subprocess
import re
from urllib.parse import unquote


class Config:
    # TODO: load config from file
    def __init__(self):
        self.hostName = "localhost"
        self.serverPort = 8080
        self.mtv_dl_binary = "mtv_dl"
        self.mtv_dl_args = []


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # TODO: add "/favicon.ico"
        print(self.path)
        if self.path == "/":
            self.send_file("index.html")
        # elif self.path == "/search.js":
        #     self.send_file("search.js")
        elif self.path.startswith("/search"):
            self.mtv_dl_dump()
        elif self.path.startswith("/download"):
            self.mtv_dl_download()

    def send_file(self, filename):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(open(filename, "rb").read())

    def mtv_dl_dump(self):
        # TODO: implement error handling
        # TODO: use better handling of GET parameters
        m = re.search(r"/search\?query=(.*)", self.path)

        query = unquote(m.group(1))

        # TODO: This gives you remote code execution!
        #       sanitize inputs before running the command
        cmd = ["mtv_dl", "-r 24", "dump", query]
        print(f"Starting mtv_dl: {' '.join(cmd)}")
        json = subprocess.check_output(cmd)
        print("mtv_dl finished")
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(json)

    def mtv_dl_download(self):
        # TODO: implement error handling
        # TODO: implement queing, mtv_dl can only handle one download at a time
        # TODO: use better handling of GET parameters
        m = re.search(r"/download\?hash=(.*)", self.path)
        hash = m.group(1)
        cmd = ["mtv_dl", "-r 23", "download", f"hash={hash}"]
        print(f"Downloading {hash}")
        print(f"Starting mtv_dl: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        print(f"Download {hash} completed.")
        self.send_response(200)
        self.send_header("Content-type", "text/text")
        self.end_headers()
        self.wfile.write("Download started.".encode("utf-8"))


if __name__ == "__main__":
    config = Config()
    webServer = HTTPServer((config.hostName, config.serverPort), MyServer)
    print("Server started http://%s:%s" % (config.hostName, config.serverPort))
    # TODO: auto-update database on startup and every 24 hours
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
