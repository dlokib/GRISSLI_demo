#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import json
import socket
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from queue import PriorityQueue

from .data import ThreadSafeDict, ThreadSafeMultiDict


SERVER_PATH = './'
SERVER_FILE = 'server.pipe'
SERVER_PIPE = "".join((SERVER_PATH, SERVER_FILE))

class FSEventHandler(FileSystemEventHandler):
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.observer = Observer()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            self.observer.unschedule_all()
            self.observer.stop()

    def watch(self):
        self.observer.schedule(self, self.folder, recursive=False)
        self.observer.start()
        self.observer.join()


class Handler(threading.Thread):
    def __init__(self):
        super(Handler, self).__init__()

        self.pointers = ThreadSafeDict()
        self.requests = PriorityQueue(128)
        self.waitings = ThreadSafeMultiDict()

        self.start()

    def run(self):
        while True:
            if os.path.exists(SERVER_PIPE):
                try:
                    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    server.connect(SERVER_PIPE)

                    def incoming():
                        while True:
                            data = server.recv(2048)

                            if not data or 'close' == data:
                                break

                            with self.waitings as waitings:
                                message = json.loads(data.decode())
                                if 'id' in message:
                                    if waitings.verify(message['id'],
                                                       message['command']):
                                        pointer = message.pop('id')
                                        if pointer in self.pointers:
                                            self.pointers[pointer].response(
                                                json.dumps(message,
                                                    separators =\
                                                    (',', ':')).encode())
                                        waitings.remove(pointer,
                                                        message['command'])
                                    
                                else:
                                    pointers = set(self.pointers.keys()) -\
                                               set(waitings.keys())
                                    for pointer in pointers:
                                        self.pointers[pointer].response(data)

                    def outgoing():
                        while True:
                            _, request = self.requests.get(block = True)

                            if isinstance(request, str):
                                if 'break' == request:
                                    break

                            with self.waitings as waitings:
                                waitings.append(request['id'], request['command'])
 
                                message = json.dumps(request,
                                                     separators = (',', ':'))

                                server.send(message.encode())

                    incoming_thread = threading.Thread(name = 'incoming',
                                                       target = incoming)
                    outgoing_thread = threading.Thread(name = 'outgoing',
                                                       target = outgoing)

                    incoming_thread.start()
                    outgoing_thread.start()

                    incoming_thread.join()
                    self.requests.put((0, 'break'), block = True)
                    outgoing_thread.join()
                except OSError as e:
                    os.remove(SERVER_PIPE)

                server.close()
            else:
                FSEventHandler(SERVER_PATH, SERVER_FILE).watch()

    def register(self, client):
        handler = self

        class Pointer:
            def __iter__(self):
                return client.__iter__()

            def request(self, command):
                handler.requests.put((1, {'id' : id(self),
                                          'command' : command.decode()}),
                                     block = True)

            def response(self, data):
                client.send(data)

        pointer = Pointer()
        with self.pointers as pointers:
            pointers[id(pointer)] = pointer

        return pointer

    def unregister(self, client):
        with self.pointers as pointers:
            self.waitings.remove_all(id(client))

            del pointers[id(client)]

handler = Handler()
