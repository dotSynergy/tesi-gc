import configparser

config = configparser.ConfigParser()
config['MAVLINK']	= {'baudrate':	'57600',
					   'device':	'/dev/ttyUSB0'}

config['WS'] 		= {'schema': 	'wss://',
					   'domain':	'dotsynergy.ddns.net',
					   'port': 		':8000',
					   'folder': 	'/drone'}

with open('../.config', 'w') as configfile:
	config.write(configfile)