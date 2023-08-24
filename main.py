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

# check for arduino connection
with open("config.json", "r") as config_file:
    config = json.load(config_file)
arduino_port = config["fes_port"]
success_threshold = config["fes_acceptable_dly"]
try:
    ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
    ArduinoSerial.close()
    ArduinoSerial.open()
    print("arduino is conected")
except:
    ArduinoSerial = False


flag = 'go'
activations = []
targets = []
global flag, activations, targets

class ThreadClass(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(list)
    def run(self):
        while True:
            global ArduinoSerial

            with open("user.json", "r") as user_file:
                user_info = json.load(user_file)
            user = {
                "license": user_info["license"],
                "client_id": user_info["client_id"],
                "client_secret": user_info["client_secret"],
                "debit": user_info["debit"]
            }

            with open("config.json", "r") as config_file:
                config = json.load(config_file)

            if config["key_push"] != "-": key_push = "Push: " + config["key_push"]
            else:key_push = ""
            if config["key_pull"] != "-": key_pull = "Pull: " + config["key_pull"]
            else: key_pull = ""
            if config["key_lift"] != "-":key_lift = "Lift: " + config["key_lift"]
            else:key_lift = ""
            if config["key_left"] != "-": key_left = "Left: " + config["key_left"]
            else: key_left = ""
            if config["key_right"] != "-":key_right = "Right: " + config["key_right"]
            else:key_right = ""
            if config["dev1_act"] != "-":dev1_act = "Device 1: " + config["dev1_act"]
            else:dev1_act = ""
            if config["dev2_act"] != "-":dev2_act = "Device 2: " + config["dev2_act"]
            else:dev2_act = ""

            ard_connection = check_arduino_connection()
            try:
                c = Cortex(user, debug_mode=False)
                t = train.Train()
                c.bind(new_com_data=t.on_new_data)
                c.do_prepare_steps()
                c.sub_request(['sys'])
                while True:
                    if config["key_push"] != "-":key_push = "Push: " + config["key_push"]
                    else:key_push = ""
                    if config["key_pull"] != "-":key_pull = "Pull: " + config["key_pull"]
                    else:key_pull = ""
                    if config["key_lift"] != "-":key_lift = "Lift: " + config["key_lift"]
                    else:key_lift = ""
                    if config["key_left"] != "-":key_left = "Left: " + config["key_left"]
                    else:key_left = ""
                    if config["key_right"] != "-":key_right = "Right: " + config["key_right"]
                    else:key_right = ""
                    if config["dev1_act"] != "-":dev1_act = "Device 1: " + config["dev1_act"]
                    else:dev1_act = ""
                    if config["dev2_act"] != "-":dev2_act = "Device 2: " + config["dev2_act"]
                    else: dev2_act = ""

                    ard_connection = check_arduino_connection()
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
                    result_dic = json.loads(new_data)
                    if "com" in result_dic:
                        com_data = {}
                        com_data['action'] = result_dic['com'][0]
                        com_data['power'] = result_dic['com'][1]
                        com_data['time'] = result_dic['time']
                        progress_label = com_data['action']
                        progress_val = int(100 * com_data['power'])
                        headset = True
                        arduino_con = ard_connection

                        keys = {"key_push": key_push, "key_pull": key_pull, "key_lift": key_lift, "key_left": key_left,
                                "key_right": key_right}
                        devs = {'dev1_act': dev1_act, 'dev2_act': dev2_act}
                        update_vals = [progress_val, progress_label, keys, devs, headset, arduino_con]
                        self.progress.emit(update_vals)
                        # time.sleep(.01)
            except:
                print('except')
                progress_label = "--"
                progress_val = 0
                headset = False
                arduino_con = ard_connection

                keys = {"key_push": key_push, "key_pull": key_pull, "key_lift": key_lift, "key_left": key_left,
                                "key_right": key_right}
                devs = {'dev1_act': dev1_act, 'dev2_act': dev2_act}
                update_vals = [progress_val, progress_label, keys, devs, headset, arduino_con]
                self.progress.emit(update_vals)
                # time.sleep(.01)


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)

        # self.menu.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.keyboard.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(0), self.update_borders('keyboard')])
        self.smarthome.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(1), self.update_borders('smart')])
        self.fes.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(2), self.update_borders('fes')])
        self.other.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(3), self.update_borders('other')])
        self.settings.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(4), self.update_borders('settings')])
        self.hlp.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(5), self.update_borders('help')])

        # Button presses in each page
        # keyboard page
        self.keyStartBtn.clicked.connect(lambda: start_thread("keyboard"))
        self.keyPauseBtn.clicked.connect(lambda: stop_thread())
        self.keyCheckBtn.clicked.connect(lambda: self.set_headset_status())

        # smart-home page
        self.smartCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.smartStartBtn.clicked.connect(lambda: start_thread("smart-home"))
        self.smartPauseBtn.clicked.connect(lambda: stop_thread())

        # FES page
        self.fesCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.fesStartBtn.clicked.connect(lambda: start_thread("fes"))
        self.fesPauseBtn.clicked.connect(lambda: stop_thread())
        self.fesManualOnBtn.clicked.connect(lambda: manual_start(ArduinoSerial))
        self.fesManualOffBtn.clicked.connect(lambda: manual_stop(ArduinoSerial))
        self.fesReportBtn.clicked.connect(lambda: generate_report(success_threshold, activations, targets))

        # other page
        self.paintLaunchBtn.clicked.connect(lambda: launch_app("BCI Paint"))
        self.gamingLaunchBtn.clicked.connect(lambda: launch_app("BCI Gaming"))

        # settings page
        self.saveSettingsBtn.clicked.connect(lambda: self.update_config_file())

        # help page
        self.openManualBtn.clicked.connect(lambda: launch_app("manual"))

        # update ui preset values
        self.update_ui_parameters()
        self.set_arduino_status()
        self.runner()

    def update_borders(self, tab):
        self.keyboard.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.smarthome.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.fes.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.other.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.settings.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.hlp.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")

        if tab == 'keyboard':
            self.keyboard.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'smart':
            self.smarthome.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'fes':
            self.fes.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'other':
            self.other.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'settings':
            self.settings.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'help':
            self.hlp.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")

    def update_ui_parameters(self):

        '''
            this function updates all the preset values for UI parameters. these values are read from a json file:
            config.json
        '''

        # load previous settings options
        print("updating json file")
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        activation_threshold = config["activation_threshold"]
        activation_delay = config["activation_delay"]
        key_push = config["key_push"]
        key_pull = config["key_pull"]
        key_lift = config["key_lift"]
        key_left = config["key_left"]
        key_right = config["key_right"]
        dev1_act = config["dev1_act"]
        dev2_act = config["dev2_act"]
        dev1_ip = config["dev1_ip"]
        dev2_ip = config["dev2_ip"]
        fes_on = config["fes_on"]
        fes_off = config["fes_off"]
        fes_port = config["fes_port"]
        fes_acceptable_dly = config["fes_acceptable_dly"]
        fes_min_dly = config["fes_min_dly"]
        smart_on_period = config["smart_on_period"]

        # load Emotiv user info
        with open("user.json", "r") as user_file:
            user_info = json.load(user_file)
        user = {
            "license": user_info["license"],
            "client_id": user_info["client_id"],
            "client_secret": user_info["client_secret"],
            "debit": user_info["debit"]
        }

        # set initial values for the UI
        self.emotivThrshldSlider.setValue(int(activation_threshold))
        self.emotivDlySpinBox.setValue(int(activation_delay))

        emotiv_cmnds = ["-", "push", "pull", "lift", "left", "light"]
        key_mappings = ["-", "w", "a", "s", "d", "up", "down", "left", "right", "enter", "space", "1", "2", "3", "4",
                        "5", "q", "e", "f", "g", "h"]
        self.keyMapPushCombo.setCurrentIndex(key_mappings.index(key_push))
        self.keyMapPullCombo.setCurrentIndex(key_mappings.index(key_pull))
        self.keyMapLiftCombo.setCurrentIndex(key_mappings.index(key_lift))
        self.keyMapLeftCombo.setCurrentIndex(key_mappings.index(key_left))
        self.keyMapRightCombo.setCurrentIndex(key_mappings.index(key_right))
        self.dev1ActCombo.setCurrentIndex(emotiv_cmnds.index(dev1_act))
        self.dev2ActCombo.setCurrentIndex(emotiv_cmnds.index(dev2_act))
        self.dev1IpLine.setText(str(dev1_ip))
        self.dev2IpLine.setText(str(dev2_ip))
        self.fesOnCombo.setCurrentIndex(emotiv_cmnds.index(fes_on))
        self.fesOffCombo.setCurrentIndex(emotiv_cmnds.index(fes_off))
        self.ComPortLine.setText(str(fes_port))
        self.trgtActDlySpin.setValue(int(fes_acceptable_dly))
        self.minDlySpin.setValue(int(fes_min_dly))
        self.smartSpinBox.setValue(int(smart_on_period))

    def update_config_file(self):
        '''
            this function updates config.json file with new parameters changed by the user on the UI
        '''
        config = {}
        emotiv_cmnds = ["-", "push", "pull", "lift", "left", "light"]
        key_mappings = ["-", "w", "a", "s", "d", "up", "down", "left", "right", "enter", "space", "1", "2", "3", "4",
                        "5", "q", "e", "f", "g", "h"]
        config["activation_threshold"] = self.emotivThrshldSlider.value()
        config["activation_delay"] = self.emotivDlySpinBox.value()
        config["key_push"] = key_mappings[self.keyMapPushCombo.currentIndex()]
        config["key_pull"] = key_mappings[self.keyMapPullCombo.currentIndex()]
        config["key_lift"] = key_mappings[self.keyMapLiftCombo.currentIndex()]
        config["key_left"] = key_mappings[self.keyMapLeftCombo.currentIndex()]
        config["key_right"] = key_mappings[self.keyMapRightCombo.currentIndex()]
        config["dev1_act"] = emotiv_cmnds[self.dev1ActCombo.currentIndex()]
        config["dev2_act"] = emotiv_cmnds[self.dev2ActCombo.currentIndex()]
        config["dev1_ip"] = self.dev1IpLine.text()
        config["dev2_ip"] = self.dev2IpLine.text()
        config["fes_on"] = emotiv_cmnds[self.fesOnCombo.currentIndex()]
        config["fes_off"] = emotiv_cmnds[self.fesOffCombo.currentIndex()]
        config["fes_port"] = self.ComPortLine.text()
        config["fes_acceptable_dly"] = self.trgtActDlySpin.value()
        config["fes_min_dly"] = self.minDlySpin.value()
        config["smart_on_period"] = self.smartSpinBox.value()
        json.dump(config, open("config.json", "w"), indent=4, sort_keys=True)
        if config["key_push"] != "-":
            key_push = "Push: " + config["key_push"]
        else:
            key_push = ""
        if config["key_pull"] != "-":
            key_pull = "Pull: " + config["key_pull"]
        else:
            key_pull = ""
        if config["key_lift"] != "-":
            key_lift = "Lift: " + config["key_lift"]
        else:
            key_lift = ""
        if config["key_left"] != "-":
            key_left = "Left: " + config["key_left"]
        else:
            key_left = ""
        if config["key_right"] != "-":
            key_right = "Right: " + config["key_right"]
        else:
            key_right = ""
        if config["dev1_act"] != "-":
            dev1_act = "Device 1: " + config["dev1_act"]
        else:
            dev1_act = ""
        if config["dev2_act"] != "-":
            dev2_act = "Device 2: " + config["dev2_act"]
        else:
            dev2_act = ""
        self.keyStatLabel.setText(f"Current key mapping:     {key_push}      {key_pull}      "
                                     f"{key_lift}       {key_left}      {key_right}")
        self.smartStatLabel.setText(f"Device activations:    {dev1_act}      {dev2_act}")




    def set_headset_status(self):
        stat = check_headset_connection()
        if stat:
            self.keyHeadLabel.setText("Emotiv headset is connected!")
            self.smartHeadLabel.setText("Emotiv headset is connected!")
            self.fesHeadLabel.setText("Emotiv headset is connected!")
        else:
            self.keyHeadLabel.setText("Emotiv headset is NOT connected!")
            self.keyHeadLabel.setStyleSheet("color:red;")
            self.smartHeadLabel.setText("Emotiv headset is NOT connected!")
            self.smartHeadLabel.setStyleSheet("color:red;")
            self.fesHeadLabel.setText("Emotiv headset is NOT connected!")
            self.fesHeadLabel.setStyleSheet("color:red;")

    def set_arduino_status(self):
        arduino_Stat = check_arduino_connection
        if arduino_Stat:
            self.fesStatLabel.setText("Hub box is connected!")
        else:
            self.fesStatLabel.setText("Hub box is NOT connected!")

    def update_ui(self, update_vals):
        [progress_val, progress_label, keys, devs, headset, arduino_con] = update_vals
        self.keyLabel.setText(progress_label)
        self.keyProgressBar.setValue(progress_val)
        self.smartLabel.setText(progress_label)
        self.smartProgressBar.setValue(progress_val)
        self.fesLabel.setText(progress_label)
        self.fesProgressBar.setValue(progress_val)
        self.keyStatLabel.setText(f"Current key mapping:     {keys['key_push']}      {keys['key_pull']}      "
                                     f"{keys['key_lift']}       {keys['key_left']}      {keys['key_right']}")
        self.smartStatLabel.setText(f"Device activations:    {devs['dev1_act']}      {devs['dev2_act']}")
        if headset:
            self.keyHeadLabel.setText("Emotiv headset is connected!")
            self.smartHeadLabel.setText("Emotiv headset is connected!")
            self.fesHeadLabel.setText("Emotiv headset is connected!")
            self.keyHeadLabel.setStyleSheet("color:white;")
            self.smartHeadLabel.setStyleSheet("color:white;")
            self.fesHeadLabel.setStyleSheet("color:white;")
        else:
            self.keyLabel.setText("--")
            self.keyProgressBar.setValue(0)
            self.smartLabel.setText("--")
            self.smartProgressBar.setValue(0)
            self.fesLabel.setText("--")
            self.fesProgressBar.setValue(0)
            self.keyHeadLabel.setText("Emotiv headset is NOT connected!")
            self.keyHeadLabel.setStyleSheet("color:red;")
            self.smartHeadLabel.setText("Emotiv headset is NOT connected!")
            self.smartHeadLabel.setStyleSheet("color:red;")
            self.fesHeadLabel.setText("Emotiv headset is NOT connected!")
            self.fesHeadLabel.setStyleSheet("color:red;")
        if arduino_con:
            self.fesStatLabel.setText("Hub box connected!")
            self.fesStatLabel.setStyleSheet("color:white;")
        else:
            self.fesStatLabel.setText("Hub box NOT connected!")
            self.fesStatLabel.setStyleSheet("color:red;")


    def runner(self):
        self.thread = QThread()
        self.worker = ThreadClass()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_ui)
        self.thread.start()


def start_emotiv(output: str):
    if output == 'keyboard':
        start_thread("keyboard")

    elif output == 'smart-home':
        start_thread("smart-home")

    elif output == 'fes':
        start_thread("fes")


#


"""
 headset_thread: a thread that generates an object from the Emotiv cortex  class and 
 runs the sub_request_GRH function in an infinite while loop. this function constantly 
 reads data generated by the headset and maps it to keyboard key presses. it also emits 
 the data as a global variable called com_data in case it needs to be used by other functions 
 com_data is a dictionary containing action, power, and time_stamp of the headset recording 
"""


def headset_thread(env, ArduinoSerial):
    global flag, activations
    profile = "GRH-HomeBCI"
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    threshold = config["activation_threshold"]
    dly = config["activation_delay"]
    min_dly = config["fes_min_dly"]
    key = [config["key_push"], config["key_pull"], config["key_lift"], config["key_left"], config["key_right"]]
    triggers = [config["fes_on"], config["fes_off"]]
    device_ip = [config["dev1_ip"], config["dev2_ip"]]
    device_act = [config["dev1_act"], config["dev2_act"]]
    device_duration = config["smart_on_period"]

    with open("user.json", "r") as user_file:
        user_info = json.load(user_file)
    user = {
        "license": user_info["license"],
        "client_id": user_info["client_id"],
        "client_secret": user_info["client_secret"],
        "debit": user_info["debit"]
    }
    try:
        c = Cortex(user, debug_mode=False)
        t = train.Train()
        c.bind(new_com_data=t.on_new_data)
        c.do_prepare_steps()
        c.sub_request(['sys'])
        stream = ['com']
        profiles = c.query_profile()
        if profile not in profiles:
            status = 'create'
            c.setup_profile(profile, status)
            status = 'load'
            c.setup_profile(profile, status)
        prev = 'off'

        while True:
            prev, last_act = c.sub_request_GRH(stream, threshold, dly, key, ArduinoSerial, triggers, min_dly, flag, env,
                                               prev, device_ip, device_act, device_duration)
            if last_act:
                activations.append(last_act)
            print(activations)

    except:
        print("No headset connected!")


def start_thread(env):
    global flag
    flag = 'go'
    send_thread = threading.Thread(target=headset_thread, args=[env, ArduinoSerial], daemon=True)
    if send_thread.is_alive():
        flag = 'go'
    else:
        flag = 'go'
        send_thread.start()


def stop_thread():
    global flag
    flag = 'stop'


def set_target():
    global targets, ArduinoSerial
    try:
        ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
        ArduinoSerial.close()
        ArduinoSerial.open()
        print("arduino is conected")
    except:
        ArduinoSerial = False
    while True:
        '''
            check if data is being received from arduino
        '''
        check = check_arduino_connection()
        if check:
            time.sleep(1)
            try:
                message = ArduinoSerial.read()
                message = message.decode()
                if message == 'N':
                    targets.append([1, time.time()])
                # Clearing the input buffer for serial
                if message == '2':
                    targets.append([2, time.time()])
                if message == '3':
                    targets.append([3, time.time()])
                if message == '4':
                    targets.append([4, time.time()])
                if message == '5':
                    targets.append([5, time.time()])
                time.sleep(1)

                ArduinoSerial.reset_input_buffer()

            except:
                try:
                    ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
                    ArduinoSerial.close()
                    ArduinoSerial.open()
                except:
                    ArduinoSerial = False




# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setWindowIcon(QtGui.QIcon("logo.png"))
widget.setWindowTitle("GRH Home-BCI")
widget.show()

''' 
    headset_ui_updater thread that constantly reads data from headset and updates the progress
    bars and labels corresponding to headset readings within the UI
'''



target_recording_thread = threading.Thread(target=set_target, args=(), daemon=True)
target_recording_thread.start()


try:
    sys.exit(app.exec_())
except:
    print("Exiting")
