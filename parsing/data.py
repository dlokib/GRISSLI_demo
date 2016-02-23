#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import threading

lock = threading.Lock()


class ThreadSafeDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __enter__(self):
        lock.acquire()

        return self

    def __exit__(self, type, value, traceback):
        lock.release()


class ThreadSafeMultiDict:
    def __init__(self, *args, **kwargs):
        self.__data = {}

    def __enter__(self):
        lock.acquire()

        return self

    def __exit__(self, type, value, traceback):
        lock.release()

    def keys(self):
        return self.__data.keys()

    def append(self, key, value):
        if key not in self.__data:
            self.__data[key] = set([value])
        else:
            self.__data[key].add(value)

    def remove(self, key, value):
        if key in self.__data:
            if value in self.__data[key]:
                self.__data[key].remove(value)

                if not self.__data[key]:
                    del self.__data[key]

    def remove_all(self, key):
        if key in self.__data:
            del self.__data[key]

    def verify(self, key, value):
        return value in self.__data.setdefault(key, set())
