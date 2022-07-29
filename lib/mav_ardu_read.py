#!/usr/bin/env python

import sys, os
from optparse import OptionParser
from pymavlink import mavutil

from lib.blackboard import MAVMessage

cur_lat = 0.0
cur_lng = 0.0
cur_alt = 0
is_airborne = False


def handle_heartbeat(msg):
	global is_airborne
	mode = mavutil.mode_string_v10(msg)
	is_armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
	is_enabled = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_GUIDED_ENABLED
	if not msg.type == mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER:
		is_airborne = (is_armed > 0) & ((msg.system_status & mavutil.mavlink.MAV_STATE_ACTIVE) > 0)

def message_bb(bb, pos: int, name: str, var):

	if not bb.contains(pos):

		m = MAVMessage(pos)
		m.lat = cur_lat
		m.lng = cur_lng
		m.alt = cur_alt
		m.is_airborne = is_airborne

		bb.produce(m)

	bb.modify(pos, name, var)

def read_loop(m, bb):

	global cur_lng
	global cur_lat
	global cur_alt

	while(True):

		# grab a mavlink message
		msg = m.recv_match(blocking=False)
		if not msg:
			continue

		# handle the message based on its type
		msg_type = msg.get_type()

		if msg_type == "BAD_DATA":
			if mavutil.all_printable(msg.data):
				#sys.stdout.write(msg.data)
				sys.stdout.flush()
		elif msg_type == "ARDU_TEMP":
			message_bb(bb, msg.cnt, 'temp', msg.temp)
		elif msg_type == "ARDU_TEMP_EXT":
			message_bb(bb, msg.cnt, 'temp_ext', msg.temp)
		elif msg_type == "ARDU_HUM":
			message_bb(bb, msg.cnt, 'hum', msg.hum)
		elif msg_type == "ARDU_HUM_EXT":
			message_bb(bb, msg.cnt, 'hum_ext', msg.hum)
		elif msg_type == "ARDU_LIGHT":
			message_bb(bb, msg.cnt, 'light', msg.light)
		elif msg_type == "ARDU_AIR_PPM":
			message_bb(bb, msg.cnt, 'air_ppm', msg.ppm)
		elif msg_type == "GLOBAL_POSITION_INT":
			cur_lat = msg.lat/10000000
			cur_lng = msg.lon/10000000
			cur_alt = msg.alt/1000
		elif msg_type == "HEARTBEAT":
			handle_heartbeat(msg)

		#else: print 'Msg not recognized, %s' % msg_type

def start_read(*args):

	conf = args[0]
	bb = args[1]

	opts = {}

	opts['device']  = conf['device'] if 'device' in conf else None
	opts['baudrate'] = conf['baudrate'] if 'baudrate' in conf else 57600
	opts['rate'] = conf['rate'] if 'rate' in conf else 1

	if opts['device'] is None:
		print("You must specify a serial device\n")
		sys.exit(1)

	# create a mavlink serial instance
	master = mavutil.mavlink_connection(opts['device'], baud=opts['baudrate'])

	# wait for the heartbeat msg to find the system ID
	master.wait_heartbeat()

	print("Heartbeat from system (system %u component %u)" %(master.target_system, master.target_system))

	# request data to be sent at the given rate
	master.mav.request_data_stream_send(master.target_system, 158, 
		mavutil.mavlink.MAV_DATA_STREAM_ALL, opts['rate'], 4)

	# enter the data loop
	read_loop(master, bb)