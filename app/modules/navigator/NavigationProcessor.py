#!/usr/bin/python
import time
import redis


RedisServer = redis.StrictRedis(host='localhost', port=6379, db=0)
RedisServer.set('Navigation.State', 'debug')
print RedisServer.get('Navigation.State')
time.sleep(120)
