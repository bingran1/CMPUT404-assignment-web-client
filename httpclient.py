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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        get = urllib.parse.urlparse(url)
        if get.port:
            port = get.port
        else:
            port = 80
        return (get.hostname, port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split_data = data[0].split('\r\n')
        code = split_data[0].split(' ')[1]
        print('code123')
        print(code)
        return int(code)

    def get_headers(self,data):
        headers = data[0]
        return headers

    def get_body(self, data):
        body = data[1]
        return body
    
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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port = self.get_host_port(url) 
        self.connect(host, port)

        parse = urllib.parse.urlparse(url)
        if (parse.path == ''):
            path = '/'
        else:
            path = parse.path
        messgae = 'GET ' + path + ' HTTP/1.1\r\n' + 'Host: ' + host + '\r\n\r\n'
        print('check111')
        print(messgae)
        self.sendall(messgae)
        receive_str = self.recvall(self.socket)
    
        data = receive_str.split('\r\n\r\n')
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parse = urllib.parse.urlparse(url)
        host, port = self.get_host_port(url) 
        self.connect(socket.gethostbyname(parse.hostname), port)
       
        #parse = urllib.parse.urlparse(url)
        if (parse.path == ''):
            path = '/'
        else:
            path = parse.path
 
        if args == None:
            args = ''
        else:
            args = urllib.parse.urlencode(args)
        content_len = len(args)
        print('start1')
        message1 = 'POST ' + path + ' HTTP/1.1\r\n' + 'Host: ' + host + '\r\n'
        message2 = 'Content-Type: application/x-www-form-urlencoded\r\n' 
        message3 = 'Content-Length: ' + str(content_len) + '\r\n\r\n' + args
        message = message1 + message2 + message3
        print('check222')
        print(message)
        self.sendall(message)
        receive_str = self.recvall(self.socket)
        data = receive_str.split('\r\n\r\n')
        
        body = self.get_body(data)
        print('data999')
        print(receive_str)
        code = self.get_code(data)
        self.close()
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
