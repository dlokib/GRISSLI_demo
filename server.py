#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import json
import time
import sched
import django
import socket
import datetime
import threading
import http.client
import lxml.html as html

from queue import PriorityQueue
from urllib.parse import urlparse


SERVER_PATH = './'
SERVER_FILE = 'server.pipe'
SERVER_PIPE = "".join((SERVER_PATH, SERVER_FILE))

XPATH_META = '/html/head/meta[@charset]'
XPATH_TITLE = '/html/head/title'
XPATH_H1 = '(/html/body//h1)[1]'

class Commands:
    def __init__(self):
        pass

    @staticmethod
    def history():
        result = []
        tasks = Task.objects.count()

        for data in Result.objects.order_by('-id')[:tasks][::-1]:
            result.append(data.dictionary())

        return result

class Connection:
    def __init__(self):
        self.address = ''
        self.channel = None

        self.__lock = threading.Lock()

    def set(self, channel, address):
        self.address = address
        self.channel = channel

    def __enter__(self):
        self.__lock.acquire()

        return self

    def __exit__(self, type, value, traceback):
        self.__lock.release()

class Handler(threading.Thread):
    def __init__(self):
        super(Handler, self).__init__()

        self.client = None

        self.start()

    def run(self):
        queue = PriorityQueue(128)
        connection = Connection()

        class Client:
            def __init__(self):
                pass

            def send(self, message):
                with connection as conn:
                    data = json.dumps(message, separators = (',', ':'))

                    if conn.channel:
                        conn.channel.send(data.encode())

        self.client = Client()

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SERVER_PIPE)

        while True:
            server.listen(1)

            connection.set(*server.accept())

            def incoming():
                while True:
                    data = connection.channel.recv(2048)

                    if not data:
                        break

                    message = json.loads(data.decode())

                    queue.put((1, message), block = True)

            def outgoing():
                while True:
                    _, request = queue.get(block = True)

                    if isinstance(request, str):
                        if 'break' == request:
                            break

                    if hasattr(Commands, request['command']):
                        request['data'] = getattr(Commands,
                                                  request['command'])()

                    self.client.send(request)

            incoming_thread = threading.Thread(name = 'incoming',
                                               target = incoming)
            outgoing_thread = threading.Thread(name = 'outgoing',
                                               target = outgoing)

            incoming_thread.start()
            outgoing_thread.start()

            incoming_thread.join()
            queue.put((0, 'break'), block = True)
            outgoing_thread.join()

            with connection as conn:
                conn.set(None, '')


class Filler:
    def __init__(self, relation):
        self.relation = relation

        self.relation.status = Status.objects.get(id = 1)
        self.relation.timestamp = time.mktime(datetime.datetime.now().\
                                              timetuple())

    def meta(self, element):
        charset = element.attrib['charset'].strip()

        try:
            codec = Codec.objects.get(name = charset)
        except:
            codec = Codec(name = charset)
            codec.save()

        self.relation.codec = codec

    def title(self, element):
        self.relation.title = element.text_content().strip()

    def h1(self, element):
        self.relation.header = element.text_content().strip()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

    django.setup()

    if os.path.exists(SERVER_PIPE):
        os.remove(SERVER_PIPE)

    handler = Handler()

    from parsing.models import *

    while True:
        def processing(task):
            result = Result(task = task, codec = None)

            try:
                url = urlparse(task.url)

                connection = http.client.HTTPSConnection(url.netloc)
                connection.request("GET", url.path)
                response = connection.getresponse()

                if response.status == 200:
                    filler = Filler(result)

                    page = html.fromstring(response.read().decode())
                    for element in page.xpath('|'.join((XPATH_META,
                                                        XPATH_TITLE,
                                                        XPATH_H1))):
                        if hasattr(filler, element.tag):
                            getattr(filler, element.tag)(element)

                connection.close()
            except:
                result.status = Status.objects.get(id = 2)

            result.save()
            handler.client.send({'command' : 'insert',
                                 'data' : [result.dictionary(), ]})

        time.sleep(300)

        handler.client.send({'command' : 'update'})

        scheduler = sched.scheduler(time.time, time.sleep)
        for task in Task.objects.all():
            scheduler.enter(task.timeshift, 1, processing, argument=(task,))

        scheduler.run()

    os.remove(SERVER_PIPE)
