#!/usr/bin/env python

class MAVMessage(object):

	temp: float = None
	temp_ext: float = None
	hum: float = None
	hum_ext: float = None
	light: int = None
	air_ppm: int = None
	lat: int = None
	lng: int = None
	alt: int = None

	def __init__(self, cnt):
		self.cnt = cnt

	def full(self):
		return not None in {self.temp, self.temp_ext,
							self.hum, self.hum_ext,
							self.light, self.air_ppm}

	def __str__(self):
		return("MAVMessage temp:% f temp_ext:% f hum:% f hum_ext:% f" \
				"light:% d air_ppm:% d lat:% f lng:% f alt:% d" % (self.temp, self.temp_ext,
							self.hum, self.hum_ext,
							self.light, self.air_ppm,
							self.lat, self.lng, self.alt))

class MAVMessagesBlackboard(object):

	# max messages to store, does not count ready to be
	# consume ones
	_max: int = 5

	def __init__(self):
		self.msgs = dict()
		self.subscribers = set()

	#blackboard pattern

	def __check_full(self, msg: MAVMessage):
		if msg.full():
			self.dispatch(msg)

	def produce(self, msg: MAVMessage):

		if self.contains(msg.cnt):
			return msg

		self.msgs[msg.cnt] = msg

		self.__check_full(msg)

		# code to look for unfinished messages past the _max 
		# number of messages and remove only unfinished ones
		l = len(self.msgs.keys())
		while l > self._max:
			for i in sorted(self.msgs.keys()):
				if l == self._max: continue

				if not self.full(i):
					self.consume(i)

				l = l-1

		return msg

	def modify(self, pos: int, name: str, var):
		if(pos in self.msgs):
			setattr(self.msgs[pos], name, var)
			self.__check_full(self.msgs[pos])

	def consume(self, pos: int):
		return self.msgs.pop(pos)

	def peek(self, pos: int):
		return self.msgs[pos]

	def full(self, pos: int):
		return self.msgs[pos].full()

	def keys(self):
		return self.msgs.keys()

	def contains(self, pos: int):
		return pos in self.msgs.keys()

	# observable pattern

	def register(self, who):
		self.subscribers.add(who)

	def unregister(self, who):
		self.subscribers.discard(who)

	def dispatch(self, message):
		for subscriber in self.subscribers:
			subscriber.update(message)


if __name__ == '__main__':

	bb = MAVMessagesBlackboard()

	for i in range(12):
		m1 = MAVMessage(i+5)
		m1.temp = 1.9

		bb.produce(m1)

		bb.modify(i+5, 'air_ppm', 1.5)
		bb.modify(i+5, 'light', 1.5)
		bb.modify(i+5, 'temp_ext', 1.5)
		bb.modify(i+5, 'hum_ext', 1.5)
		bb.modify(i+5, 'hum', 1.5)


	print(bb.keys())

	#if(bb.full(12)): bb.consume(12)
	print(bb.msgs)

