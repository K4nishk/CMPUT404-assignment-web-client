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

# python3 -m http.server 27601 --bind 127.0.0.1

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
        """
        FUNCTIONALITY:
            * This method is used to extract the host, port and the path of the request

        ARGUMENTS:
            * self: The instance of the class.
            * url: The string entered as an argument during the execution of this python file.

        RETURNS:
            * host: A string containing the host name
            * port: A string containing the port addressed, 80 if not mentioned
            * path: A string containing the path of the requested file
        """

        parsedUrl = urllib.parse.urlparse(url)

        port = parsedUrl.port
        if port is None:
            port = 80

        host = parsedUrl.hostname
        path = parsedUrl.path

        if path == "":
            path = "/"

        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        """
        FUNCTIONALITY:
            * This method is used to get the status code of the location

        ARGUMENTS:
            * self: The instance of the class.
            * data: A string containing the data received from the server.

        RETURNS:
            * code: An integer value containing the status code of the HTTP response
        """

        headers = self.get_headers(data)
        request = headers.split("\r\n")[0]
        code = request.split(" ")[1]

        return int(code)

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        """
        FUNCTIONALITY:
            * This method is used to get the body from the response

        ARGUMENTS:
            * self: The instance of the class.
            * data: A string containing the data received from the server.

        RETURNS:
            * body: A string containg the body of the response
        """

        data = data.split("\r\n\r\n")

        body = ""
        if (len(data) > 1):
            body = data[1]

        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def preparePayload(self, method, host, path, body=""):
        """
        FUNCTIONALITY:
            * This method is used to generate the payload to be sent to the server.

        ARGUMENTS:
            * self: The instance of the class.
            * method: A string containing GET or POST method
            * host: A string containing the host name
            * path: A string containing the path to the file
            * body: A string containing the information to be sent over to the server.
                If the method is GET then the body will be empty and if the method is POST
                then the body will be the arguments passed during the execution of this file.

        RETURNS:
            * payload: A string containing the payload to be sent to the server
        """

        specificHeaders = ""

        if method == "GET":
            specificHeaders = "Accept-Charset: utf-8"
        elif method == "POST":
            specificHeaders = "Content-Type: application/x-www-form-urlencoded"
        else:
            # Unsupported method
            sys.exit()

        length = "0"
        if body != "":
            length = str(len(body))
        specificHeaders += "\r\nContent-Length: " + length

        payload = f'{method} {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\n{specificHeaders}\r\nConnection: close\r\n\r\n{body}\r\n'
        
        return payload

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
        """
        FUNCTIONALITY:
            * This method is used to implement the GET request for the client

        ARGUMENTS:
            * self: The instance of the class.
            * url: A string containing the url of the requested server
            * args: Additional arguments provided

        RETURNS:
            * An object of HTTPResponse class containing the status code and the body of
                the response received from the server
        """

        # respond with the code and the body read
        host, port, path = self.get_host_port(url)
        
        # establish a connection
        self.connect(host, port)

        body = ""
        if args is not None:
            body = urllib.parse.urlencode(args)
        
        # Send the payload
        payload = self.preparePayload("GET", host, path)
        self.sendall(payload)

        # get the data
        data = str(self.recvall(self.socket))
        
        # close the opened socket
        self.close()
        
        code = self.get_code(data)
        body = self.get_body(data)

        print(code)
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        """
        FUNCTIONALITY:
            * This method is used to implement the POST request for the client

        ARGUMENTS:
            * self: The instance of the class.
            * url: A string containing the url of the requested server
            * args: Additional arguments provided

        RETURNS:
            * An object of HTTPResponse class containing the status code and the body of
                the response received from the server
        """

        # respond with the code and the body read
        host, port, path = self.get_host_port(url)
        
        # establish a connection
        self.connect(host, port)

        body = ""
        if args is not None:
            body = urllib.parse.urlencode(args)

        # Send the payload
        payload = self.preparePayload("POST", host, path, body)
        self.sendall(payload)

        # get the data
        data = str(self.recvall(self.socket))
        
        # close the opened socket
        self.close()
        
        code = self.get_code(data)
        body = self.get_body(data)

        print(code)
        print(body)
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
