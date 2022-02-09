#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from inspect import ArgSpec
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

from urllib3 import get_host

PORT = 80

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body

class HTTPClient(object):
    def get_host(self,url):
        try:
            return urllib.parse.urlparse(url).netloc.split(":")[0]
        except:
            return None

    def get_port(self, url):
        try:
            return int(urllib.parse.urlparse(url).netloc.split(":")[1])
        except:
            return None

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            lines = data.splitlines()
            code = lines[0].split()[1]
        except:
            code = None

        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        # body appears afte the headers
        # the headers and body of an http response are separated by an empty line
        try:
            body_index = 0
            for line in data.splitlines():
                if line == "":
                    body_index += 1
                    break
                body_index += 1

            return data.splitlines()[body_index]
        except:
            return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        # return buffer.decode('utf-8')
        # try ascii instead of latin1
        return buffer.decode('latin1')
        # return buffer

    def GET(self, url, args=None):
        code = 500
        body = ""

        host = self.get_host(url)
        port = self.get_port(url)

        # print("host: ", host)
        # print("port: ", port)

        if host == None:
            return HTTPResponse(404, None)

        self.connect(host, port)

        url_parsed = urllib.parse.urlparse(url)

        request = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(url_parsed.path, url_parsed.netloc)
        self.sendall(request)
        data = self.recvall(self.socket)

        self.close()

        # print(data)

        code = self.get_code(data)
        body = self.get_body(data)

        # print("code: ", code)
        # print("body: ", body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host = self.get_host(url)
        port = self.get_port(url)

        if host == None:
            return HTTPResponse(404, None)

        self.connect(host, port)

        url_parsed = urllib.parse.urlparse(url)

        # post_data = {'a':'aaaaaaaaaaaaa',
        #     'b':'bbbbbbbbbbbbbbbbbbbbbb',
        #     'c':'c',
        #     'd':'012345\r67890\n2321321\n\r'}

        post_data = "a=aaaaaaaaaaaaa&b=bbbbbbbbbbbbbbbbbbbbbb&c=c&d=012345\r67890\n2321321\n\r"

        request = 'POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: \
            application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}'\
                .format(url_parsed.path, url_parsed.netloc, len(post_data), post_data)
        self.sendall(request)
        data = self.recvall(self.socket)

        self.close()

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
