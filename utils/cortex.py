
import websocket  # 'pip install websocket-client' for install
import json
import ssl
import time
from pydispatch.dispatch import Dispatcher
from utils.press import press
from pynput.keyboard import Key, Controller
from utils.handle_dev import handle_device
from utils.spotify import spotify_handler
from utils.blth_handler import send_data, connect_to_blth, find_blth_ports
import asyncio
import queue
from pynput.mouse import Controller as mouse_controller
from pynput.mouse import Button as mouse_Button
from utils.mouse_click import mouse_click
"""
    Emotiv Cortex class. this class includes all the required functions for handling headset data, i.e. 
    training, profile generation, connecting to emotiv cloud services, headset connection, and requesting data 
    from the headset. Cortex.sub_request_GRH function handles receiving data entries from the headset and 
    maps them to key presses. this function can be manipulated to map headset outputs to other things.
"""


# define request id
QUERY_HEADSET_ID = 1
CONNECT_HEADSET_ID = 2
REQUEST_ACCESS_ID = 3
AUTHORIZE_ID = 4
CREATE_SESSION_ID = 5
SUB_REQUEST_ID = 6
SETUP_PROFILE_ID = 7
QUERY_PROFILE_ID = 8
TRAINING_ID = 9
DISCONNECT_HEADSET_ID = 10
CREATE_RECORD_REQUEST_ID = 11
STOP_RECORD_REQUEST_ID = 12
EXPORT_RECORD_ID = 13
INJECT_MARKER_REQUEST_ID = 14
SENSITIVITY_REQUEST_ID = 15
MENTAL_COMMAND_ACTIVE_ACTION_ID = 16
MENTAL_COMMAND_BRAIN_MAP_ID = 17
MENTAL_COMMAND_TRAINING_THRESHOLD = 18
SET_MENTAL_COMMAND_ACTIVE_ACTION_ID = 19
GET_TRAINING_DATA = 20

class Cortex(Dispatcher):
    def __init__(self, user, debug_mode=False):
        url = "wss://localhost:6868"
        self.ws = websocket.create_connection(url,
                                              sslopt={"cert_reqs": ssl.CERT_NONE})
        self.user = user
        self.debug = debug_mode

    def query_headset(self):
        print('query headset --------------------------------')
        query_headset_request = {
            "jsonrpc": "2.0",
            "id": QUERY_HEADSET_ID,
            "method": "queryHeadsets",
            "params": {}
        }

        self.ws.send(json.dumps(query_headset_request, indent=4))
        result = self.ws.recv()
        result_dic = json.loads(result)

        return result_dic['result']

    def connect_headset(self, headset_id):
        print('connect headset --------------------------------')
        connect_headset_request = {
            "jsonrpc": "2.0",
            "id": CONNECT_HEADSET_ID,
            "method": "controlDevice",
            "params": {
                "command": "connect",
                "headset": headset_id
            }
        }
        self.ws.send(json.dumps(connect_headset_request, indent=4))

        # wait until connect completed
        while True:
            time.sleep(1)
            result = self.ws.recv()
            result_dic = json.loads(result)

            if self.debug:
                print('connect headset result', json.dumps(result_dic, indent=4))

            if 'warning' in result_dic:
                if result_dic['warning']['code'] == 104:
                    self.headset_id = headset_id
                    print("Connect headset " + self.headset_id + " successfully.")
                    break
                else:
                    print(result_dic['warning']['code'])

    def request_access(self):
        print('request access --------------------------------')
        request_access_request = {
            "jsonrpc": "2.0",
            "method": "requestAccess",
            "params": {
                "clientId": self.user['client_id'],
                "clientSecret": self.user['client_secret']
            },
            "id": REQUEST_ACCESS_ID
        }

        self.ws.send(json.dumps(request_access_request, indent=4))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        if result_dic.get('result') != None:
            access_granted = result_dic['result']['accessGranted']
            return access_granted
        elif result_dic.get('error') != None:
            print("Request Access get error: " + result_dic['error']['message'])
        return False

    def authorize(self):
        print('authorize --------------------------------')
        authorize_request = {
            "jsonrpc": "2.0",
            "method": "authorize",
            "params": {
                "clientId": self.user['client_id'],
                "clientSecret": self.user['client_secret'],
                "license": self.user['license'],
                "debit": self.user['debit']
            },
            "id": AUTHORIZE_ID
        }

        if self.debug:
            print('auth request \n', json.dumps(authorize_request, indent=4))

        self.ws.send(json.dumps(authorize_request))

        while True:
            result = self.ws.recv()
            result_dic = json.loads(result)
            if 'id' in result_dic:
                if result_dic['id'] == AUTHORIZE_ID:
                    if self.debug:
                        print('auth result \n', json.dumps(result_dic, indent=4))
                    self.auth = result_dic['result']['cortexToken']
                    break

    def create_session(self, auth, headset_id):
        print('create session --------------------------------')
        create_session_request = {
            "jsonrpc": "2.0",
            "id": CREATE_SESSION_ID,
            "method": "createSession",
            "params": {
                "cortexToken": self.auth,
                "headset": self.headset_id,
                "status": "active"
            }

        }

        if self.debug:
            print('create session request \n', json.dumps(create_session_request, indent=4))

        self.ws.send(json.dumps(create_session_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('create session result \n', json.dumps(result_dic, indent=4))

        self.session_id = result_dic['result']['id']

    def close_session(self):
        print('close session --------------------------------')
        close_session_request = {
            "jsonrpc": "2.0",
            "id": CREATE_SESSION_ID,
            "method": "updateSession",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "status": "close"
            }
        }

        self.ws.send(json.dumps(close_session_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('close session result \n', json.dumps(result_dic, indent=4))

    def get_cortex_info(self):
        print('get cortex version --------------------------------')
        get_cortex_info_request = {
            "jsonrpc": "2.0",
            "method": "getCortexInfo",
            "id": 100
        }

        self.ws.send(json.dumps(get_cortex_info_request))
        result = self.ws.recv()
        if self.debug:
            print(json.dumps(json.loads(result), indent=4))

    def do_prepare_steps(self):
        headsets = self.query_headset()

        if len(headsets) > 0:
            # get first element
            headset_id = headsets[0]['id']
            headset_status = headsets[0]['status']

            if headset_status != "connected":
                # connect headset
                self.connect_headset(headset_id)
            else:
                print("The headset " + headset_id + " has been connected.")
                self.headset_id = headset_id

            result = self.request_access()
            if result == True:
                self.authorize()
                self.create_session(self.auth, self.headset_id)
            else:
                print(
                    "The user has not granted access right to this application. Please use EMOTIV Launcher to proceed. Then try again.")
        else:
            print("No headset available. Please turn on a headset to proceed.")

    def disconnect_headset(self):
        print('disconnect headset --------------------------------')
        disconnect_headset_request = {
            "jsonrpc": "2.0",
            "id": DISCONNECT_HEADSET_ID,
            "method": "controlDevice",
            "params": {
                "command": "disconnect",
                "headset": self.headset_id
            }
        }

        self.ws.send(json.dumps(disconnect_headset_request))

        # wait until disconnect completed
        while True:

            time.sleep(1)
            result = self.ws.recv()
            result_dic = json.loads(result)

            if self.debug:
                print('disconnect headset result', json.dumps(result_dic, indent=4))

            if 'warning' in result_dic:
                if result_dic['warning']['code'] == 1:
                    break

    _events_ = ['new_data_labels', 'new_com_data', 'new_fe_data', 'new_eeg_data', 'new_mot_data', 'new_dev_data',
                'new_met_data', 'new_pow_data']

    def sub_request(self, stream):
        print('subscribe request --------------------------------')
        sub_request_json = {
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": stream
            },
            "id": SUB_REQUEST_ID
        }

        self.ws.send(json.dumps(sub_request_json))

        # handle subscribe response
        new_data = self.ws.recv()
        result_dic = json.loads(new_data)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        if 'sys' in stream:
            # ignored sys data
            return

        if result_dic.get('error') != None:
            print("subscribe get error: " + result_dic['error']['message'])
            return
        else:
            # handle data lable
            for stream in result_dic['result']['success']:

                stream_name = stream['streamName']
                stream_labels = stream['cols']
                # ignore com and fac data label because they are handled in on_new_data
                if stream_name != 'com' and stream_name != 'fac':
                    self.extract_data_labels(stream_name, stream_labels)

        # Handle data event
        while True:

            new_data = self.ws.recv()
            # Then emit the change with optional positional and keyword arguments
            result_dic = json.loads(new_data)
            if result_dic.get('com') != None:
                com_data = {}
                com_data['action'] = result_dic['com'][0]
                com_data['power'] = result_dic['com'][1]
                com_data['time'] = result_dic['time']

                self.emit('new_com_data', data=com_data)
            elif result_dic.get('fac') != None:
                fe_data = {}
                fe_data['eyeAct'] = result_dic['fac'][0]  # eye action
                fe_data['uAct'] = result_dic['fac'][1]  # upper action
                fe_data['uPow'] = result_dic['fac'][2]  # upper action power
                fe_data['lAct'] = result_dic['fac'][3]  # lower action
                fe_data['lPow'] = result_dic['fac'][4]  # lower action power
                fe_data['time'] = result_dic['time']
                self.emit('new_fe_data', data=fe_data)
            elif result_dic.get('eeg') != None:
                eeg_data = {}
                eeg_data['eeg'] = result_dic['eeg']
                eeg_data['eeg'].pop()  # remove markers
                eeg_data['time'] = result_dic['time']
                self.emit('new_eeg_data', data=eeg_data)
            elif result_dic.get('mot') != None:
                mot_data = {}
                mot_data['mot'] = result_dic['mot']
                mot_data['time'] = result_dic['time']
                self.emit('new_mot_data', data=mot_data)

            elif result_dic.get('dev') != None:
                dev_data = {}
                dev_data['signal'] = result_dic['dev'][1]
                dev_data['dev'] = result_dic['dev'][2]
                dev_data['batteryPercent'] = result_dic['dev'][3]
                dev_data['time'] = result_dic['time']
                self.emit('new_dev_data', data=dev_data)
            elif result_dic.get('met') != None:
                met_data = {}
                met_data['met'] = result_dic['met']
                met_data['time'] = result_dic['time']
                self.emit('new_met_data', data=met_data)
            elif result_dic.get('pow') != None:
                pow_data = {}
                pow_data['pow'] = result_dic['pow']
                pow_data['time'] = result_dic['time']
                self.emit('new_pow_data', data=pow_data)
            else:
                print(new_data)

    def sub_request_GRH(self, stream, threshold, delay, key, AT_sock, triggers, min_dly, flag, env, prev_state,
                        device_ip,device_act, device_duration, prev_wc_btn, btn_action, spotify_cmd, prev_time, latch_flags):

        print('subscribe request --------------------------------')
        sub_request_json = {
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": stream
            },
            "id": SUB_REQUEST_ID
        }
        activation = []
        self.ws.send(json.dumps(sub_request_json))

        # handle subscribe response
        new_data = self.ws.recv()
        result_dic = json.loads(new_data)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        if 'sys' in stream:
            # ignored sys data
            return

        if result_dic.get('error') != None:
            print("subscribe get error: " + result_dic['error']['message'])
            return
        else:
            # handle data label
            try:
                # print(result_dic['result'])
                for stream in result_dic['result']['success']:
                    stream_name = stream['streamName']
                    stream_labels = stream['cols']
                    # ignore com and fac data label because they are handled in on_new_data
                    if stream_name != 'com' and stream_name != 'fac':
                        self.extract_data_labels(stream_name, stream_labels)
            except:
                print('data input error55----------------------------------------------------------------')


        # Handle data event

        temp_time = prev_time
        data = ["-", 0]
        # while True:
        new_data = self.ws.recv()
        # Then emit the change with optional positional and keyword arguments
        result_dic = json.loads(new_data)
        if result_dic.get('com') != None:
            com_data = {}
            com_data['action'] = result_dic['com'][0]
            com_data['power'] = result_dic['com'][1]
            com_data['time'] = result_dic['time']
            data = [com_data['action'], com_data['power']]
            threshold = threshold
            self.emit('new_com_data', data=com_data)
            on_command = str(triggers[0])
            off_command = str(triggers[1])
            btn1_action = str(btn_action[0])
            btn2_action = str(btn_action[1])
            btn3_action = str(btn_action[2])
            btn4_action = str(btn_action[3])
            spotify_play_cmd = str(spotify_cmd[0])
            spotify_pause_cmd = str(spotify_cmd[1])
            spotify_next_cmd = str(spotify_cmd[2])
            spotify_prev_cmd = str(spotify_cmd[3])
            spotify_min_dly = spotify_cmd[4]

            if com_data['action'] == 'push' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= delay and flag != 'stop' and env == "keyboard":
                if key[0] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[0] == 'space':
                    press(Key.space)
                elif key[0] == 'enter':
                    press(Key.enter)
                elif key[0] == 'Lclick':
                    mouse_click(mouse_Button.left)
                elif key[0] == 'up':
                    press(Key.up)
                elif key[0] == 'down':
                    press(Key.down)
                elif key[0] == 'right':
                    press(Key.right)
                elif key[0] == 'left':
                    press(Key.left)
                else:
                    press((key[0]))
                prev_time = float(time.time())

            elif com_data['action'] == 'pull' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= delay and flag != 'stop'and env == "keyboard":
                if key[1] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[1] == 'space':
                    press(Key.space)
                elif key[1] == 'enter':
                    press(Key.enter)
                elif key[1] == 'Lclick':
                    mouse_click(mouse_Button.left)
                elif key[1] == 'up':
                    press(Key.up)
                elif key[1] == 'down':
                    press(Key.down)
                elif key[1] == 'right':
                    press(Key.right)
                elif key[1] == 'left':
                    press(Key.left)
                else:
                    press((key[1]))
                prev_time = float(time.time())


            elif com_data['action'] == 'lift' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= delay and flag != 'stop'and env == "keyboard":
                if key[2] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[2] == 'space':
                    press(Key.space)
                elif key[2] == 'enter':
                    press(Key.enter)
                elif key[2] == 'Lclick':
                    mouse_click(mouse_Button.left)
                elif key[2] == 'up':
                    press(Key.up)
                elif key[2] == 'down':
                    press(Key.down)
                elif key[2] == 'right':
                    press(Key.right)
                elif key[2] == 'left':
                    press(Key.left)
                else:
                    press((key[2]))
                prev_time = float(time.time())

            elif com_data['action'] == 'left' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= delay and flag != 'stop'and env == "keyboard":
                if key[3] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[3] == 'space':
                    press(Key.space)
                elif key[3] == 'enter':
                    press(Key.enter)
                elif key[3] == 'Lclick':
                    mouse_click(mouse_Button.left)
                elif key[3] == 'up':
                    press(Key.up)
                elif key[3] == 'down':
                    press(Key.down)
                elif key[3] == 'right':
                    press(Key.right)
                elif key[3] == 'left':
                    press(Key.left)
                else:
                    press((key[3]))
                prev_time = float(time.time())

            elif com_data['action'] == 'neurtal' and env == "keyboard":
                print('neutral')

            elif com_data['action'] == on_command and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= min_dly and env == "fes":
                send_data(AT_sock, "0N")
                time.sleep(.1)
                send_data(AT_sock, "0F")
                prev_time = float(time.time())
                prev_state = 'on'
                activation = (time.time())

            elif com_data['action'] == off_command and com_data['action'] != 'neutral' and 100 * float(
                    com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= min_dly and prev_state == 'on' and env == "fes":
                send_data(AT_sock, "02")
                time.sleep(.1)
                send_data(AT_sock, "0F")
                prev_time = float(time.time())
                prev_state = 'off'

            elif com_data['action'] == off_command and com_data['action'] == 'neutral' and (
                    float(time.time()) - temp_time) >= min_dly and prev_state == 'on' and env == "fes":
                send_data(AT_sock, "02")
                time.sleep(.1)
                send_data(AT_sock, "0F")
                prev_time = float(time.time())
                prev_state = 'off'

            elif com_data['action'] == spotify_play_cmd and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= spotify_min_dly and env == "spotify":
                spotify_handler("play")
                prev_time = float(time.time())

            elif com_data['action'] == spotify_pause_cmd and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= spotify_min_dly and env == "spotify":
                spotify_handler("pause")
                prev_time = float(time.time())

            elif com_data['action'] == spotify_next_cmd and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= spotify_min_dly and env == "spotify":
                spotify_handler("next")
                prev_time = float(time.time())

            elif com_data['action'] == spotify_prev_cmd and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= spotify_min_dly and env == "spotify":
                spotify_handler("previous")
                prev_time = float(time.time())

            elif com_data['action'] == device_act[0] and 100 * float(com_data['power']) >= int(threshold) and (
                    float(time.time()) - temp_time) >= delay and flag != 'stop'and env == "smart-home":
                asyncio.run(handle_device(device_ip[0], device_duration))
                prev_time = float(time.time())

            elif com_data['action'] == device_act[1] and 100 * float(com_data['power']) >= int(threshold) and (
                        float(time.time()) - temp_time) >= delay and flag != 'stop' and env == "smart-home":
                asyncio.run(handle_device(device_ip[1], device_duration))
                prev_time = float(time.time())

            elif com_data['action'] == btn1_action and 100 * float(com_data['power']) >= int(threshold) and (
                        float(time.time()) - temp_time) >= delay  and prev_wc_btn != 'btn1' and flag != 'stop'and env == "wc":

                if prev_wc_btn == 'btn1_latched':
                    time.sleep(.06)
                    send_data(AT_sock, "0F")
                    prev_wc_btn = 'off'
                    prev_time = float(time.time())

                else:
                    send_data(AT_sock, "0N")
                    # time.sleep(.1)
                    prev_wc_btn = 'btn1'
                    prev_time = float(time.time())

            elif com_data['action'] == btn2_action and 100 * float(com_data['power']) >= int(threshold) and (
                        float(time.time()) - temp_time) >= delay  and prev_wc_btn != 'btn2' and flag != 'stop'and env == "wc":
                if prev_wc_btn == 'btn2_latched':
                    time.sleep(.06)
                    send_data(AT_sock, "0F")
                    prev_wc_btn = 'off'
                    prev_time = float(time.time())

                else:
                    send_data(AT_sock, "02")
                    # time.sleep(.1)
                    prev_wc_btn = 'btn2'
                    prev_time = float(time.time())

            elif com_data['action'] == btn3_action and 100 * float(com_data['power']) >= int(threshold) and (
                        float(time.time()) - temp_time) >= delay  and prev_wc_btn != 'btn3' and flag != 'stop'and env == "wc":
                if prev_wc_btn == 'btn3_latched':
                    time.sleep(.06)
                    send_data(AT_sock, "0F")
                    prev_wc_btn = 'off'
                    prev_time = float(time.time())

                else:
                    send_data(AT_sock, "03")
                    # time.sleep(.1)
                    prev_wc_btn = 'btn3'
                    prev_time = float(time.time())

            elif com_data['action'] == btn4_action and 100 * float(com_data['power']) >= int(threshold) and (
                        float(time.time()) - temp_time) >= delay  and prev_wc_btn != 'btn4' and flag != 'stop'and env == "wc":
                if prev_wc_btn == 'btn4_latched':
                    time.sleep(.06)
                    send_data(AT_sock, "0F")
                    prev_wc_btn = 'off'
                    prev_time = float(time.time())

                else:
                    send_data(AT_sock, "04")
                    # time.sleep(.1)
                    prev_wc_btn = 'btn4'
                    prev_time = float(time.time())

            elif flag != 'stop'and env == "wc" and com_data['action'] == 'neutral':
                if prev_wc_btn == 'btn1':
                    if latch_flags[0]:
                        print('latched')
                        prev_wc_btn = 'btn1_latched'
                    else:
                        time.sleep(.06)
                        send_data(AT_sock, "0F")
                        prev_wc_btn = 'off'
                elif prev_wc_btn == 'btn2':
                    if latch_flags[1]:
                        print('latched')
                        prev_wc_btn = 'btn2_latched'
                    else:
                        time.sleep(.06)
                        send_data(AT_sock, "0F")
                        prev_wc_btn = 'off'
                elif prev_wc_btn == 'btn3':
                    if latch_flags[2]:
                        print('latched')
                        prev_wc_btn = 'btn3_latched'
                    else:
                        time.sleep(.06)
                        send_data(AT_sock, "0F")
                        prev_wc_btn = 'off'
                elif prev_wc_btn == 'btn4':
                    if latch_flags[3]:
                        print('latched')
                        prev_wc_btn = 'btn4_latched'
                    else:
                        time.sleep(.06)
                        send_data(AT_sock, "0F")
                        prev_wc_btn = 'off'

            elif flag == 'stop' and env == "wc":

                time.sleep(.06)
                send_data(AT_sock, "0F")
                prev_wc_btn = 'off'

            else:
                print('Waiting for new command')


        elif result_dic.get('fac') != None:
            fe_data = {}
            fe_data['eyeAct'] = result_dic['fac'][0]  # eye action
            fe_data['uAct'] = result_dic['fac'][1]  # upper action
            fe_data['uPow'] = result_dic['fac'][2]  # upper action power
            fe_data['lAct'] = result_dic['fac'][3]  # lower action
            fe_data['lPow'] = result_dic['fac'][4]  # lower action power
            fe_data['time'] = result_dic['time']
            self.emit('new_fe_data', data=fe_data)

        elif result_dic.get('eeg') != None:
            eeg_data = {}
            eeg_data['eeg'] = result_dic['eeg']
            eeg_data['eeg'].pop()  # remove markers
            eeg_data['time'] = result_dic['time']
            self.emit('new_eeg_data', data=eeg_data)
        elif result_dic.get('mot') != None:
            mot_data = {}
            mot_data['mot'] = result_dic['mot']
            mot_data['time'] = result_dic['time']
            self.emit('new_mot_data', data=mot_data)

        elif result_dic.get('dev') != None:
            dev_data = {}
            dev_data['signal'] = result_dic['dev'][1]
            dev_data['dev'] = result_dic['dev'][2]
            dev_data['batteryPercent'] = result_dic['dev'][3]
            dev_data['time'] = result_dic['time']
            self.emit('new_dev_data', data=dev_data)
        elif result_dic.get('met') != None:
            met_data = {}
            met_data['met'] = result_dic['met']
            met_data['time'] = result_dic['time']
            self.emit('new_met_data', data=met_data)
        elif result_dic.get('pow') != None:
            pow_data = {}
            pow_data['pow'] = result_dic['pow']
            pow_data['time'] = result_dic['time']
            self.emit('new_pow_data', data=pow_data)
        else:
            print(new_data)

        return prev_state, activation, prev_wc_btn, data, prev_time

    def extract_data_labels(self, stream_name, stream_cols):
        data = {}
        data['streamName'] = stream_name

        data_labels = []
        if stream_name == 'eeg':
            # remove MARKERS
            data_labels = stream_cols[:-1]
        elif stream_name == 'dev':
            # get cq header column except battery, signal and battery percent
            data_labels = stream_cols[2]
        else:
            data_labels = stream_cols

        data['labels'] = data_labels
        self.emit('new_data_labels', data=data)

    def query_profile(self):
        print('query profile --------------------------------')
        query_profile_json = {
            "jsonrpc": "2.0",
            "method": "queryProfile",
            "params": {
                "cortexToken": self.auth,
            },
            "id": QUERY_PROFILE_ID
        }

        if self.debug:
            print('query profile request \n', json.dumps(query_profile_json, indent=4))
            print('\n')

        self.ws.send(json.dumps(query_profile_json))

        result = self.ws.recv()
        result_dic = json.loads(result)

        print('query profile result\n', result_dic)
        print('\n')

        profiles = []
        for p in result_dic['result']:
            profiles.append(p['name'])

        print('extract profiles name only')
        print(profiles)
        print('\n')

        return profiles

    def setup_profile(self, profile_name, status):
        print('setup profile: ' + status + ' -------------------------------- ')
        setup_profile_json = {
            "jsonrpc": "2.0",
            "method": "setupProfile",
            "params": {
                "cortexToken": self.auth,
                "headset": self.headset_id,
                "profile": profile_name,
                "status": status
            },
            "id": SETUP_PROFILE_ID
        }

        if self.debug:
            print('setup profile json:\n', json.dumps(setup_profile_json, indent=4))
            print('\n')

        self.ws.send(json.dumps(setup_profile_json))

        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('result \n', json.dumps(result_dic, indent=4))
            print('\n')

    def train_request(self, detection, action, status, q):
        # print('train request --------------------------------')
        train_request_json = {
            "jsonrpc": "2.0",
            "method": "training",
            "params": {
                "cortexToken": self.auth,
                "detection": detection,
                "session": self.session_id,
                "action": action,
                "status": status
            },
            "id": TRAINING_ID
        }

        # print('training request:\n', json.dumps(train_request_json, indent=4))
        # print('\n')

        self.ws.send(json.dumps(train_request_json))

        if detection == 'mentalCommand':
            start_wanted_result = 'MC_Succeeded'
            accept_wanted_result = 'MC_Completed'
            reject_wanted_result = 'MC_Rejected'
            erase_wanted_result = 'MC_DataErased'
        if detection == 'facialExpression':
            start_wanted_result = 'FE_Succeeded'
            accept_wanted_result = 'FE_Completed'

        if status == 'start':
            wanted_result = start_wanted_result
            print('\n YOU HAVE 8 SECONDS FOR TRAIN ACTION {} \n'.format(action.upper()))

        if status == 'accept':
            wanted_result = accept_wanted_result

        if status == 'reject':
            wanted_result = reject_wanted_result

        if status == 'erase':
            wanted_result = erase_wanted_result


        # wait until success
        while True:
            result = self.ws.recv()

            result_dic = json.loads(result)

            print(json.dumps(result_dic, indent=4))

            if 'sys' in result_dic:
                # success or complete, break the wait

                if result_dic['sys'][1] == 'MC_Failed':
                    q.put(result_dic['sys'][1])
                    break
                if result_dic['sys'][1] == wanted_result:
                    q.put(result_dic['sys'][1])
                    break

    def get_training_data(self, profile_name):
        print('getting profiles trained data --------------- ')
        get_training_json = {
            "jsonrpc": "2.0",
            "method": "getTrainedSignatureActions",
            "params": {
                "cortexToken": self.auth,
                "detection": "mentalCommand",
                "profile": profile_name
            },
            "id": GET_TRAINING_DATA
        }
        self.ws.send(json.dumps(get_training_json))
        result = self.ws.recv()
        result_dic = json.loads(result)
        return result_dic

    def brain_map(self, profile_name):
        print('brain map plot --------------- ')
        brain_map_json = {
            "jsonrpc": "2.0",
            "method": "mentalCommandBrainMap",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "session": self.session_id
            }
        }
        self.ws.send(json.dumps(brain_map_json))
        result = self.ws.recv()
        result_dic = json.loads(result)
        return result_dic


    def create_record(self,
                      record_name,
                      record_description):
        print('create record --------------------------------')
        create_record_request = {
            "jsonrpc": "2.0",
            "method": "createRecord",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "title": record_name,
                "description": record_description
            },

            "id": CREATE_RECORD_REQUEST_ID
        }

        self.ws.send(json.dumps(create_record_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('start record request \n',
                  json.dumps(create_record_request, indent=4))
            print('start record result \n',
                  json.dumps(result_dic, indent=4))

        self.record_id = result_dic['result']['record']['uuid']

    def stop_record(self):
        print('stop record --------------------------------')
        stop_record_request = {
            "jsonrpc": "2.0",
            "method": "stopRecord",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id
            },

            "id": STOP_RECORD_REQUEST_ID
        }

        self.ws.send(json.dumps(stop_record_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('stop request +\n',
                  json.dumps(stop_record_request, indent=4))
            print('stop result \n',
                  json.dumps(result_dic, indent=4))

    def export_record(self,
                      folder,
                      export_types,
                      export_format,
                      export_version,
                      record_ids):

        print('export record --------------------------------')
        export_record_request = {
            "jsonrpc": "2.0",
            "id": EXPORT_RECORD_ID,
            "method": "exportRecord",
            "params": {
                "cortexToken": self.auth,
                "folder": folder,
                "format": export_format,
                "streamTypes": export_types,
                "recordIds": record_ids
            }
        }

        # "version": export_version,
        if export_format == 'CSV':
            export_record_request['params']['version'] = export_version

        if self.debug:
            print('export record request \n',
                  json.dumps(export_record_request, indent=4))

        self.ws.send(json.dumps(export_record_request))

        # wait until export record completed
        while True:
            time.sleep(1)
            result = self.ws.recv()
            result_dic = json.loads(result)

            if self.debug:
                print('export record result \n',
                      json.dumps(result_dic, indent=4))

            if 'result' in result_dic:
                if len(result_dic['result']['success']) > 0:
                    break

    def inject_marker_request(self, marker):
        print('inject marker --------------------------------')
        inject_marker_request = {
            "jsonrpc": "2.0",
            "id": INJECT_MARKER_REQUEST_ID,
            "method": "injectMarker",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "label": marker['label'],
                "value": marker['value'],
                "port": marker['port'],
                "time": marker['time']
            }
        }

        self.ws.send(json.dumps(inject_marker_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('inject marker request \n', json.dumps(inject_marker_request, indent=4))
            print('inject marker result \n',
                  json.dumps(result_dic, indent=4))
