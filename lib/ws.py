#!/usr/bin/env python

import websocket
import time
import json as JSON

from lib.blackboard import MAVMessage

class WSMessage(object):

	ws = None
	_srv = ''
	_org = ''

	def try_and_connect(self):
		# 5 retries, then die
		cnt = 0
		while cnt%5==0:
			try:
				self.ws = websocket.create_connection(self._srv,origin=self._org)
				return True
			except ConnectionRefusedError:
				cnt = cnt+1
				time.sleep(1)
		return None

	def __init__(self, conf):
		self._srv = conf['schema']+conf['domain']+conf['port']+conf['folder']
		self._org = conf['domain']
		self.try_and_connect()

	def update(self, msg: MAVMessage):
		if self.ws is None:
			if(not self.try_and_connect()):
				exit
		try:
			m = '{"action":"store", "data":%s}' % JSON.dumps(msg.__dict__)
			print (m)
			self.ws.send(m)
		except KeyboardInterrupt:
			self.ws.close("")
		except BrokenPipeError:
			print("The pipe is broken!")
			if(not self.try_and_connect()):
				exit
		except:
			print("The server is not working!")

def start_send(*args):

	conf = args[0]
	bb = args[1]

	ws = WSMessage(conf)
	bb.register(ws)