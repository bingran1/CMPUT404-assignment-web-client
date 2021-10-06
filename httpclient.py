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
    # get the host and port by using urllib.parse
    def get_host_port(self,url):
        get = urllib.parse.urlparse(url)
        # if the port exists, the return port
        # should be the value get from the url
        # if not, the port should be 80
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
        # split the first element in data by '\r\n'.
        # then split the first element of previous line returned
        # data by ' ' and pick the second element which is code
        split_data = data[0].split('\r\n')
        code = split_data[0].split(' ')[1]
        return int(code)

    def get_headers(self,data):
        # the first element of data contains both
        # code line and headers, so using parttion('\r\n')
        # will get three elements: ('code line', '\r\n', 'left lines')
        # and the left lines are headers,
        header_str = data[0]
        partition_str = header_str.partition('\r\n')
        headers = partition_str[2]
        return headers

    def get_body(self, data):
        # the second element of data is body
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
        # get host and port by calling above function
        # then connect them
        host, port = self.get_host_port(url) 
        self.connect(host, port)

        parse = urllib.parse.urlparse(url)
        # if we find that the path is empty
        # the path should become to '/'
        if (parse.path == ''):
            path = '/'
        else:
            path = parse.path
        # write message and send 
        messgae = 'GET ' + path + ' HTTP/1.1\r\n' + 'Host: ' + host + '\r\n\r\n'
        self.sendall(messgae)
        # receive data from the socket will get
        # the string contains code, headers and body
        receive_str = self.recvall(self.socket)
        # split the receive stirng into two part
        # first is code lines and headers and the second
        # part is body
        data = receive_str.split('\r\n\r\n')
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parse = urllib.parse.urlparse(url)
        # get host and port by calling above function
        # then connect them
        host, port = self.get_host_port(url) 
        self.connect(host, port)
       
        # if we find that the path is empty
        # the path should become to '/'
        if (parse.path == ''):
            path = '/'
        else:
            path = parse.path
        # if we find that the args is None
        # then it should become empty
        if args == None:
            args = ''
        else:
            args = urllib.parse.urlencode(args)
        # write message and send
        message1 = 'POST ' + path + ' HTTP/1.1\r\n' + 'Host: ' + host + '\r\n'
        message2 = 'Content-Type: application/x-www-form-urlencoded\r\n' 
        message3 = 'Content-Length: ' + str(len(args)) + '\r\n\r\n' + args
        message = message1 + message2 + message3
        self.sendall(message)
        receive_str = self.recvall(self.socket)
        data = receive_str.split('\r\n\r\n')
        
        body = self.get_body(data)
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
