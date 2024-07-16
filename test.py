<<<<<<< Updated upstream
from pynput.keyboard import Key, Controller
from pynput.keyboard import Key, Controller

import threading
import time
kb = Controller()

"""
    function for emulating key press and key hold-downs 
"""

def press_n_hold(button, duration):
    kb.press(button)
    curr = time.time()
    while time.time() - curr <= duration:
        pass
    kb.release(button)


def press(button):
    thread = threading.Thread(target=press_n_hold, args=((button), 0.1))
    thread.start()
# Press and release sp ace
press("a")
=======
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
import resources_rc
import threading
import json
import time
from utils import *
from serial import Serial
from PyQt5.QtCore import QObject, QThread, pyqtSignal

with open("user.json", "r") as user_file:
    user_info = json.load(user_file)
user = {
    "license": user_info["license"],
    "client_id": user_info["client_id"],
    "client_secret": user_info["client_secret"],
    "debit": user_info["debit"]
}

c = Cortex(user, debug_mode=False)
t = train.Train()
c.bind(new_com_data=t.on_new_data)
c.do_prepare_steps()
c.sub_request(['sys'])
stream = ['com']
sub_request_json = {
    "jsonrpc": "2.0",
    "method": "subscribe",
    "params": {
        "cortexToken": c.auth,
        "session": c.session_id,
        "streams": stream
    },
    "id": 6
}
c.ws.send(json.dumps(sub_request_json))
new_data = c.ws.recv()
training_action = 'neutral'
t.train_mc("1",training_action,1)

>>>>>>> Stashed changes

#
# profile_name = 'testprof'
#
# number_of_train = 1
# # try:
# c = Cortex(user, debug_mode=False)
# t = train.Train()
# c.bind(new_com_data=t.on_new_data)
# c.do_prepare_steps()
# c.sub_request(['sys'])
# t.load_profile(profile_name)
# training_action = 'neutral'
# # except:
# #     print('ridi')
#     # t.load_profile(profile_name)
#     #
#     # training_action = 'neutral'
#     # t.train_mc(profile_name,training_action,number_of_train)
#     # t.unload_profile(profile_name)
#     # t.live(profile_name)