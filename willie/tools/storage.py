# coding=utf8
"""Functions for managing storage."""
from __future__ import unicode_literals
from __future__ import absolute_import
import os.path
import threading
import json

directory = os.path.join(os.getcwd(), 'storage', 'modules', 'storage')
lock = threading.Lock()
def put(key, data):
    lock.acquire()
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, key+'.dat')
        file = open(path, 'w')
        json.dump(data, file)
        file.close()
    except:
        print "Error writing %.dat" % (key)
    finally:
        lock.release()
	
def get(key):
    lock.acquire()
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, key+'.dat')
        if os.path.isfile(path):
            file = open(path, 'r')
            try:
                data = json.load(file)
            except:
                file.close()
                return None
            file.close()
            return data
        else:
            return None
    except:
        print "Error reading %.dat" % (key)
    finally:
        lock.release()
