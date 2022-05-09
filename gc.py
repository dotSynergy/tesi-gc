#!/usr/bin/env python

from lib.mav_ardu_read import start_read
from lib.ws import start_send
from lib.blackboard import MAVMessage, MAVMessagesBlackboard
from config.conf import config

import logging
from threading import Thread
import time

def main():

    bb = MAVMessagesBlackboard()

    print('starting threads...')
    mav_thread = Thread(target=start_read, args=([config['MAVLINK'], bb]))
    ws_thread = Thread(target=start_send, args=([config['WS'], bb]))

    mav_thread.start()
    ws_thread.start()
    print('started!\n')

    time.sleep(2)

    mav_thread.join()
    ws_thread.join()
    print('stopped!')


if __name__ == '__main__':
    main()