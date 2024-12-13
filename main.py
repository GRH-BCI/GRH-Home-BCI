import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
import resources_rc
import threading
import json
import time
from utils import *
from serial import Serial
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRect, QPropertyAnimation
from PyQt5 import QtGui
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFrame
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# check for arduino connection
with open("config.json", "r") as config_file:
    config = json.load(config_file)

arduino_connection.find_arduino_port()
arduino_port = config["fes_port"]
success_threshold = config["fes_acceptable_dly"]
try:
    ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
    ArduinoSerial.close()
    ArduinoSerial.open()
    print("arduino is conected")
except:
    ArduinoSerial = False

global activations, targets

activations = []
targets = []


class WelcomeScreen(QDialog):
    update_signal = pyqtSignal(list)
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.ArduinoSerial = ArduinoSerial
        print(self.ArduinoSerial)
        self.profile_name = ''
        self.time_left_int = 10
        self.myTimer = QtCore.QTimer(self)
        self.flag = "-"
        self.environment = 'keyboard'
        self.latch_flag = [False, False, False, False]
        # self.menu.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.training.clicked.connect(
            lambda: [self.stackedWidget.setCurrentIndex(0), self.update_borders('TrainingPage')])
        self.keyboard.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(1), self.update_borders('keyboard')])
        self.smarthome.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(2), self.update_borders('smart')])
        self.fes.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(3), self.update_borders('fes')])
        self.other.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(4), self.update_borders('other')])
        self.wheelchair.clicked.connect(
            lambda: [self.stackedWidget.setCurrentIndex(5), self.update_borders('wheelchair')])
        self.spotify.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(6), self.update_borders('spotify')])
        self.settings.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(7), self.update_borders('settings')])
        self.hlp.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(8), self.update_borders('help')])

        # Button presses in each page
        # training page
        self.NeutralLabelCounter = 0
        self.NeutralLabel.setText(str(self.NeutralLabelCounter))
        self.PushLabelCounter = 0
        self.PushLabel.setText(str(self.PushLabelCounter))
        self.PullLabelCounter = 0
        self.PullLabel.setText(str(self.PullLabelCounter))
        self.LiftLabelCounter = 0
        self.LiftLabel.setText(str(self.LiftLabelCounter))
        self.DropLabelCounter = 0
        self.DropLabel.setText(str(self.DropLabelCounter))
        self.current_cmd = ''
        self.BrainMapBtn.clicked.connect(lambda: self.plot_brain_map())
        self.SelectImageBtn.clicked.connect(lambda: self.openImagePopUp())
        self.NeutTrn.clicked.connect(
            lambda: [self.resize_animation('neutral'), self.t.train_mc('neutral'), self.toggle_training_btn('training'),
                     self.update_counter_label('neutral'), self.startTimer()])
        self.PushTrn.clicked.connect(
            lambda: [self.resize_animation('push'), self.t.train_mc('push'), self.toggle_training_btn('training'),
                     self.update_counter_label('push'), self.startTimer()])
        self.PullTrn.clicked.connect(
            lambda: [self.resize_animation('pull'), self.t.train_mc('pull'), self.toggle_training_btn('training'),
                     self.update_counter_label('pull'), self.startTimer()])
        self.LiftTrn.clicked.connect(
            lambda: [self.resize_animation('lift'), self.t.train_mc('lift'), self.toggle_training_btn('training'),
                     self.update_counter_label('lift'), self.startTimer()])
        self.DropTrn.clicked.connect(
            lambda: [self.resize_animation('drop'), self.t.train_mc('drop'), self.toggle_training_btn('training'),
                     self.update_counter_label('drop'), self.startTimer()])

        self.AccBtn.clicked.connect(lambda: [self.accept_training(self.current_cmd), self.toggle_training_btn('train')])
        self.RejBtn.clicked.connect(lambda: [self.reject_training(self.current_cmd), self.toggle_training_btn('train')])
        self.NeutralDelBtn.clicked.connect(
            lambda: [self.delete_training('neutral'), self.update_counter_label('neutral-delete')])
        self.PushDelBtn.clicked.connect(
            lambda: [self.delete_training('push'), self.update_counter_label('push-delete')])
        self.PullDelBtn.clicked.connect(
            lambda: [self.delete_training('pull'), self.update_counter_label('pull-delete')])
        self.LiftDelBtn.clicked.connect(
            lambda: [self.delete_training('lift'), self.update_counter_label('lift-delete')])
        self.DropDelBtn.clicked.connect(
            lambda: [self.delete_training('drop'), self.update_counter_label('drop-delete')])

        self.toggle_training_btn('profile')
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self.GraphFrame)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_facecolor("grey")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.figure.tight_layout(pad=0)

        self.CrtProfile.clicked.connect(lambda: self.CreateProfile())

        # keyboard page
        self.keyStartBtn.clicked.connect(lambda: self.start_thread("keyboard", self.profile_name))
        self.keyPauseBtn.clicked.connect(lambda: self.stop_thread())
        self.keyCheckBtn.clicked.connect(lambda: self.set_headset_status())

        # smart-home page
        self.smartCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.smartStartBtn.clicked.connect(lambda: self.start_thread("smart-home", self.profile_name))
        self.smartPauseBtn.clicked.connect(lambda: self.stop_thread())

        # FES page
        self.fesCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.fesStartBtn.clicked.connect(lambda: self.start_thread("fes", self.profile_name))
        self.fesPauseBtn.clicked.connect(lambda: self.stop_thread())
        self.fesManualOnBtn.clicked.connect(lambda: manual_start(self.ArduinoSerial))
        self.fesManualOffBtn.clicked.connect(lambda: manual_stop(self.ArduinoSerial))
        self.fesReportBtn.clicked.connect(lambda: generate_report(success_threshold, activations, targets))

        # other page
        self.paintLaunchBtn.clicked.connect(lambda: launch_app("BCI Paint"))
        self.gamingLaunchBtn.clicked.connect(lambda: launch_app("BCI Gaming"))

        # wheelchair page
        self.WCCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.WCStartBtn.clicked.connect(lambda: self.start_thread("wc", self.profile_name))
        self.WCPauseBtn.clicked.connect(lambda: self.stop_thread())
        self.WCCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.LatchBtn1.clicked.connect(lambda: self.latch_mode(1))
        self.LatchBtn2.clicked.connect(lambda: self.latch_mode(2))
        self.LatchBtn3.clicked.connect(lambda: self.latch_mode(3))
        self.LatchBtn4.clicked.connect(lambda: self.latch_mode(4))
        self.WCManualOnBtn_1.pressed.connect(lambda: manual_btn_control(self.ArduinoSerial, 1))
        self.WCManualOnBtn_1.released.connect(lambda: manual_btn_control(self.ArduinoSerial, 0))
        self.WCManualOnBtn_2.pressed.connect(lambda: manual_btn_control(self.ArduinoSerial, 2))
        self.WCManualOnBtn_2.released.connect(lambda: manual_btn_control(self.ArduinoSerial, 0))
        self.WCManualOnBtn_3.pressed.connect(lambda: manual_btn_control(self.ArduinoSerial, 3))
        self.WCManualOnBtn_3.released.connect(lambda: manual_btn_control(self.ArduinoSerial, 0))
        self.WCManualOnBtn_4.pressed.connect(lambda: manual_btn_control(self.ArduinoSerial, 4))
        self.WCManualOnBtn_4.released.connect(lambda: manual_btn_control(self.ArduinoSerial, 0))

        # spotify page
        self.spotifyPlayBtn.clicked.connect(lambda: spotify_handler("play"))
        self.spotifyPauseBtn_2.clicked.connect(lambda: spotify_handler("pause"))
        self.spotifyNextBtn.clicked.connect(lambda: spotify_handler("next"))
        self.spotifyPrevBtn.clicked.connect(lambda: spotify_handler("previous"))
        self.spotifyCheckBtn.clicked.connect(lambda: self.set_headset_status())
        self.spotifyStartBtn.clicked.connect(lambda: self.start_thread("spotify", self.profile_name))
        self.spotifyPauseBtn.clicked.connect(lambda: self.stop_thread())

        # settings page
        self.saveSettingsBtn.clicked.connect(lambda: self.save_config())
        self.ConnectApiBtn.clicked.connect(lambda: connect_spotify())

        # help page
        self.openManualBtn.clicked.connect(lambda: launch_app("manual"))

        # update ui preset values
        self.set_ui_parameters()
        self.set_arduino_status()
        self.set_headset_status()
        self.thread = QThread()
        self.update_signal.connect(self.update_progress_bar)

    def set_ui_parameters(self):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        self.activation_threshold = config["activation_threshold"]
        self.activation_delay = config["activation_delay"]
        self.key_push = config["key_push"]
        self.key_pull = config["key_pull"]
        self.key_lift = config["key_lift"]
        self.key_drop = config["key_drop"]
        self.dev1_act = config["dev1_act"]
        self.dev2_act = config["dev2_act"]
        self.dev1_ip = config["dev1_ip"]
        self.dev2_ip = config["dev2_ip"]
        self.fes_on = config["fes_on"]
        self.fes_off = config["fes_off"]
        self.fes_port = config["fes_port"]
        self.fes_acceptable_dly = config["fes_acceptable_dly"]
        self.fes_min_dly = config["fes_min_dly"]
        self.smart_on_period = config["smart_on_period"]
        self.btn_1 = config["btn_1"]
        self.btn_2 = config["btn_2"]
        self.btn_3 = config["btn_3"]
        self.btn_4 = config["btn_4"]
        self.spot_play = config['spot_play']
        self.spot_pause = config['spot_pause']
        self.spot_next = config['spot_next']
        self.spot_prev = config['spot_prev']
        self.spot_min_dly = config['spot_min_dly']

        # load Emotiv user info
        with open("user.json", "r") as user_file:
            user_info = json.load(user_file)
        self.user = {
            "license": user_info["license"],
            "client_id": user_info["client_id"],
            "client_secret": user_info["client_secret"],
            "debit": user_info["debit"]
        }

        with open("spotify.json", "r") as spot_config_file:
            spot_config = json.load(spot_config_file)
        self.spotify_client_ID = spot_config['client_id']
        self.spotify_client_secret = spot_config['client_secret']
        self.spotify_redirect_url = spot_config['redirect_uri']

        # set initial values for the UI
        self.emotivThrshldSlider.setValue(int(self.activation_threshold))
        self.emotivDlySpinBox.setValue(int(self.activation_delay))

        emotiv_cmnds = ["-", "push", "pull", "lift", "drop"]
        key_mappings = ["-", "w", "a", "s", "d", "up", "down", "left", "right", "enter", "space", "Lclick", "1", "2",
                        "3", "4",
                        "5", "q", "e", "f", "g", "h"]
        spotify_cmnds = ["-", "push", "pull", "lift", "drop"]
        self.keyMapPushCombo.setCurrentIndex(key_mappings.index(self.key_push))
        self.keyMapPullCombo.setCurrentIndex(key_mappings.index(self.key_pull))
        self.keyMapLiftCombo.setCurrentIndex(key_mappings.index(self.key_lift))
        self.keyMapdropCombo.setCurrentIndex(key_mappings.index(self.key_drop))
        self.dev1ActCombo.setCurrentIndex(emotiv_cmnds.index(self.dev1_act))
        self.dev2ActCombo.setCurrentIndex(emotiv_cmnds.index(self.dev2_act))
        self.dev1IpLine.setText(str(self.dev1_ip))
        self.dev2IpLine.setText(str(self.dev2_ip))
        self.fesOnCombo.setCurrentIndex(emotiv_cmnds.index(self.fes_on))
        self.fesOffCombo.setCurrentIndex(emotiv_cmnds.index(self.fes_off))
        self.ComPortLine.setText(str(self.fes_port))
        self.trgtActDlySpin.setValue(int(self.fes_acceptable_dly))
        self.minDlySpin.setValue(int(self.fes_min_dly))
        self.smartSpinBox.setValue(int(self.smart_on_period))
        self.wcCombo_1.setCurrentIndex(emotiv_cmnds.index(self.btn_1))
        self.wcCombo_2.setCurrentIndex(emotiv_cmnds.index(self.btn_2))
        self.wcCombo_3.setCurrentIndex(emotiv_cmnds.index(self.btn_3))
        self.wcCombo_4.setCurrentIndex(emotiv_cmnds.index(self.btn_4))
        self.SpotifyPlayCombo.setCurrentIndex(spotify_cmnds.index(self.spot_play))
        self.SpotifyPauseCombo.setCurrentIndex(spotify_cmnds.index(self.spot_pause))
        self.SpotifyNextCombo.setCurrentIndex(spotify_cmnds.index(self.spot_next))
        self.SpotifyPrevCombo.setCurrentIndex(spotify_cmnds.index(self.spot_prev))
        self.SpotifyTokenLine.setText(str(self.spotify_client_ID))
        self.SpotifySecretLine.setText(str(self.spotify_client_secret))
        self.SpotifyUrlLine.setText(str(self.spotify_redirect_url))
        key_push = "Push: " + str(self.key_push)
        key_pull = "Pull: " + str(self.key_pull)
        key_lift = "Lift: " + str(self.key_lift)
        key_drop = "drop: " + str(self.key_drop)
        dev1_act = "Device 1: " + str(self.dev1_act)
        dev2_act = "Device 2: " + str(self.dev2_act)
        spot_play = self.spot_play
        spot_pause = self.spot_pause
        spot_next = self.spot_next
        spot_prev = self.spot_prev
        self.keyStatLabel.setText(f"Current key mapping:     {key_push}      {key_pull}      "
                                  f"{key_lift}       {key_drop}")
        self.smartStatLabel.setText(f"Device activations:    {dev1_act}      {dev2_act}")
        self.spotifyStatLabel.setText(
            f"Play:{spot_play}    Pause:{spot_pause}     Next:{spot_next}      Previous:{spot_prev}")

        spot_config_file.close()
        user_file.close()
        config_file.close()

    def save_config(self):
        '''
            this function updates config.json file with new parameters changed by the user on the UI
        '''
        config = {}
        emotiv_cmnds = ["-", "push", "pull", "lift", "drop"]
        key_mappings = ["-", "w", "a", "s", "d", "up", "down", "left", "right", "enter", "space", "Lclick", "1", "2",
                        "3", "4",
                        "5", "q", "e", "f", "g", "h"]
        spotify_mapping = ["-", 'push', 'pull', 'lift', 'drop']
        config["activation_threshold"] = self.emotivThrshldSlider.value()
        config["activation_delay"] = self.emotivDlySpinBox.value()
        config["key_push"] = key_mappings[self.keyMapPushCombo.currentIndex()]
        config["key_pull"] = key_mappings[self.keyMapPullCombo.currentIndex()]
        config["key_lift"] = key_mappings[self.keyMapLiftCombo.currentIndex()]
        config["key_drop"] = key_mappings[self.keyMapdropCombo.currentIndex()]
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
        config["btn_1"] = emotiv_cmnds[self.wcCombo_1.currentIndex()]
        config["btn_2"] = emotiv_cmnds[self.wcCombo_2.currentIndex()]
        config["btn_3"] = emotiv_cmnds[self.wcCombo_3.currentIndex()]
        config["btn_4"] = emotiv_cmnds[self.wcCombo_4.currentIndex()]
        config["spot_play"] = spotify_mapping[self.SpotifyPlayCombo.currentIndex()]
        config["spot_pause"] = spotify_mapping[self.SpotifyPauseCombo.currentIndex()]
        config["spot_next"] = spotify_mapping[self.SpotifyNextCombo.currentIndex()]
        config["spot_prev"] = spotify_mapping[self.SpotifyPrevCombo.currentIndex()]
        config["spot_min_dly"] = self.SpotifyMinDelaySpin.value()
        spotify_config = {}
        spotify_config['client_id'] = self.SpotifyTokenLine.text()
        spotify_config['client_secret'] = self.SpotifySecretLine.text()
        spotify_config['redirect_uri'] = self.SpotifyUrlLine.text()
        json.dump(config, open("config.json", "w"), indent=4, sort_keys=False)
        json.dump(spotify_config, open("spotify.json", "w"), indent=4, sort_keys=False)
        self.activation_threshold = config["activation_threshold"]
        self.activation_delay = config["activation_delay"]
        self.key_push = config["key_push"]
        self.key_pull = config["key_pull"]
        self.key_lift = config["key_lift"]
        self.key_drop = config["key_drop"]
        self.dev1_act = config["dev1_act"]
        self.dev2_act = config["dev2_act"]
        self.dev1_ip = config["dev1_ip"]
        self.dev2_ip = config["dev2_ip"]
        self.fes_on = config["fes_on"]
        self.fes_off = config["fes_off"]
        self.fes_port = config["fes_port"]
        self.fes_acceptable_dly = config["fes_acceptable_dly"]
        self.fes_min_dly = config["fes_min_dly"]
        self.smart_on_period = config["smart_on_period"]
        self.btn_1 = config["btn_1"]
        self.btn_2 = config["btn_2"]
        self.btn_3 = config["btn_3"]
        self.btn_4 = config["btn_4"]
        self.spot_play = config['spot_play']
        self.spot_pause = config['spot_pause']
        self.spot_next = config['spot_next']
        self.spot_prev = config['spot_prev']
        self.spot_min_dly = config['spot_min_dly']

        key_push = "Push: " + str(self.key_push)
        key_pull = "Pull: " + str(self.key_pull)
        key_lift = "Lift: " + str(self.key_lift)
        key_drop = "drop: " + str(self.key_drop)
        dev1_act = "Device 1: " + str(self.dev1_act)
        dev2_act = "Device 2: " + str(self.dev2_act)
        spot_play = self.spot_play
        spot_pause = self.spot_pause
        spot_next = self.spot_next
        spot_prev = self.spot_prev

        self.keyStatLabel.setText(f"Current key mapping:     {key_push}      {key_pull}      "
                                  f"{key_lift}       {key_drop}")
        self.smartStatLabel.setText(f"Device activations:    {dev1_act}      {dev2_act}")
        self.spotifyStatLabel.setText(
            f"Play:{spot_play}    Pause:{spot_pause}     Next:{spot_next}      Previous:{spot_prev}")

    def toggle_training_btn(self, status):
        if status == 'profile':
            self.NeutTrn.hide()
            self.NeutralLabel.hide()
            self.PushTrn.hide()
            self.PushLabel.hide()
            self.PullTrn.hide()
            self.PullLabel.hide()
            self.LiftTrn.hide()
            self.LiftLabel.hide()
            self.DropTrn.hide()
            self.DropLabel.hide()
            self.AccBtn.hide()
            self.RejBtn.hide()
            self.BrainMapBtn.hide()
            self.NeutralDelBtn.hide()
            self.PushDelBtn.hide()
            self.PullDelBtn.hide()
            self.LiftDelBtn.hide()
            self.DropDelBtn.hide()
            self.keyStartBtn.setDisabled(True)
            self.keyPauseBtn.setDisabled(True)
            self.smartStartBtn.setDisabled(True)
            self.smartPauseBtn.setDisabled(True)
            self.fesStartBtn.setDisabled(True)
            self.fesPauseBtn.setDisabled(True)
            self.WCStartBtn.setDisabled(True)
            self.WCPauseBtn.setDisabled(True)
            self.spotifyStartBtn.setDisabled(True)
            self.spotifyPauseBtn.setDisabled(True)
        elif status == 'train':
            self.NeutTrn.show()
            self.NeutralLabel.show()
            self.PushTrn.show()
            self.PushLabel.show()
            self.PullTrn.show()
            self.PullLabel.show()
            self.LiftTrn.show()
            self.LiftLabel.show()
            self.DropTrn.show()
            self.DropLabel.show()
            self.NeutralDelBtn.show()
            self.PushDelBtn.show()
            self.PullDelBtn.show()
            self.LiftDelBtn.show()
            self.DropDelBtn.show()
            self.NeutTrn.setDisabled(False)
            self.PushTrn.setDisabled(False)
            self.PullTrn.setDisabled(False)
            self.LiftTrn.setDisabled(False)
            self.DropTrn.setDisabled(False)
            self.AccBtn.hide()
            self.RejBtn.hide()
            self.BrainMapBtn.show()
            self.CrtProfile.setDisabled(True)
            self.keyStartBtn.setDisabled(False)
            self.keyPauseBtn.setDisabled(False)
            self.smartStartBtn.setDisabled(False)
            self.smartPauseBtn.setDisabled(False)
            self.fesStartBtn.setDisabled(False)
            self.fesPauseBtn.setDisabled(False)
            self.WCStartBtn.setDisabled(False)
            self.WCPauseBtn.setDisabled(False)
            self.spotifyStartBtn.setDisabled(False)
            self.spotifyPauseBtn.setDisabled(False)
        elif status == 'training':
            self.NeutTrn.setDisabled(True)
            self.PushTrn.setDisabled(True)
            self.PullTrn.setDisabled(True)
            self.LiftTrn.setDisabled(True)
            self.DropTrn.setDisabled(True)
            self.CrtProfile.setDisabled(True)
        elif status == 'started':
            self.keyStartBtn.setDisabled(True)
            self.keyPauseBtn.setDisabled(False)
            self.smartStartBtn.setDisabled(True)
            self.smartPauseBtn.setDisabled(False)
            self.fesStartBtn.setDisabled(True)
            self.fesPauseBtn.setDisabled(False)
            self.WCStartBtn.setDisabled(True)
            self.WCPauseBtn.setDisabled(False)
            self.spotifyStartBtn.setDisabled(True)
            self.spotifyPauseBtn.setDisabled(False)
        elif status == 'paused':
            self.keyStartBtn.setDisabled(False)
            self.keyPauseBtn.setDisabled(True)
            self.smartStartBtn.setDisabled(False)
            self.smartPauseBtn.setDisabled(True)
            self.fesStartBtn.setDisabled(False)
            self.fesPauseBtn.setDisabled(True)
            self.WCStartBtn.setDisabled(False)
            self.WCPauseBtn.setDisabled(True)
            self.spotifyStartBtn.setDisabled(False)
            self.spotifyPauseBtn.setDisabled(True)

    def latch_mode(self, BtnNum):
        if BtnNum == 1:
            if self.LatchBtn1.isChecked():
                self.latch_flag[0] = True
            else:
                self.latch_flag[0] = False
        elif BtnNum == 2:
            if self.LatchBtn2.isChecked():
                self.latch_flag[1] = True
            else:
                self.latch_flag[1] = False
        elif BtnNum == 3:
            if self.LatchBtn2.isChecked():
                self.latch_flag[2] = True
            else:
                self.latch_flag[2] = False
        elif BtnNum == 4:
            if self.LatchBtn2.isChecked():
                self.latch_flag[3] = True
            else:
                self.latch_flag[3] = False

    def openImagePopUp(self):
        path = QFileDialog.getOpenFileNames(self, 'Choose mental image object:', '.\\Assets', "Image files (*.png)")
        sprite = Image.open(path[0][0])
        if 500 <= sprite.width <= 550 and 500 <= sprite.height <= 550:
            self.SpritePath = path[0][0]
            SpritePixMap = QPixmap(self.SpritePath)
            self.TrainSprite.setPixmap(SpritePixMap)
        else:
            warningMsg = QMessageBox()
            warningMsg.setWindowTitle("Oops Wrong image!")
            warningMsg.setText("Image has to be 500x500 pixels and in png format!")
            warningMsg.exec_()

    def startTimer(self):
        self.time_left_int = 10
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.setInterval(1000)
        self.myTimer.start()

    def timerTimeout(self):
        self.time_left_int -= 1
        if self.time_left_int == 0:
            self.AccBtn.show()
            self.RejBtn.show()
            self.myTimer.stop()
            self.myTimer.timeout.disconnect(self.timerTimeout)
        self.timerLabel.setText(str(self.time_left_int))

    def btnstate(self):
        if self.WCManualOnBtn_1.isChecked():
            manual_btn_control(self.ArduinoSerial, 1)
        else:
            manual_btn_control(self.ArduinoSerial, 0)
        if self.WCManualOnBtn_2.isChecked():
            manual_btn_control(self.ArduinoSerial, 2)
        else:
            manual_btn_control(self.ArduinoSerial, 0)
        if self.WCManualOnBtn_3.isChecked():
            manual_btn_control(self.ArduinoSerial, 3)
        else:
            manual_btn_control(self.ArduinoSerial, 0)
        if self.WCManualOnBtn_4.isChecked():
            manual_btn_control(self.ArduinoSerial, 4)
        else:
            manual_btn_control(self.ArduinoSerial, 0)

    def resize_animation(self, cmd):
        frame_obj = self.TrainSprite
        if cmd == 'push':
            self.animation_1 = QPropertyAnimation(frame_obj, b'size')
            self.myTimer = QtCore.QTimer(self)
            self.animation_1.setStartValue(QSize(frame_obj.width(), frame_obj.height()))
            self.animation_1.setEndValue(QSize(round(frame_obj.width() / 3), round(frame_obj.height() / 3)))
            self.animation_1.setDuration(9500)
            self.animation_2 = QPropertyAnimation(frame_obj, b'size')
            self.animation_2.setEndValue(QSize(round(frame_obj.width()), round(frame_obj.height())))
            self.animation_2.setDuration(500)
            self.anim_group = QSequentialAnimationGroup()
            self.anim_group.addAnimation(self.animation_1)
            self.anim_group.addAnimation(self.animation_2)
            self.anim_group.start()
        elif cmd == 'pull':
            self.animation_1 = QPropertyAnimation(frame_obj, b'size')
            self.myTimer = QtCore.QTimer(self)
            self.animation_1.setStartValue(QSize(round(frame_obj.width() / 3), round(frame_obj.height() / 3)))
            self.animation_1.setEndValue(QSize(round(frame_obj.width()), round(frame_obj.height())))
            self.animation_1.setDuration(9500)
            self.animation_2 = QPropertyAnimation(frame_obj, b'size')
            self.animation_2.setEndValue(QSize(round(frame_obj.width()), round(frame_obj.height())))
            self.animation_2.setDuration(500)
            self.anim_group = QSequentialAnimationGroup()
            self.anim_group.addAnimation(self.animation_1)
            self.anim_group.addAnimation(self.animation_2)
            self.anim_group.start()
        elif cmd == 'drop':
            self.animation_1 = QPropertyAnimation(frame_obj, b'pos')
            self.myTimer = QtCore.QTimer(self)
            self.animation_1.setStartValue(QPoint(frame_obj.x(), frame_obj.y()))
            self.animation_1.setEndValue(QPoint(round(frame_obj.x()), round(frame_obj.y() * 2)))
            self.animation_1.setDuration(9500)
            self.animation_2 = QPropertyAnimation(frame_obj, b'pos')
            self.animation_2.setEndValue(QPoint(round(frame_obj.x()), round(frame_obj.y())))
            self.animation_2.setDuration(500)
            self.anim_group = QSequentialAnimationGroup()
            self.anim_group.addAnimation(self.animation_1)
            self.anim_group.addAnimation(self.animation_2)
            self.anim_group.start()
        elif cmd == 'lift':
            self.animation_1 = QPropertyAnimation(frame_obj, b'pos')
            self.myTimer = QtCore.QTimer(self)
            self.animation_1.setStartValue(QPoint(frame_obj.x(), frame_obj.y()))
            self.animation_1.setEndValue(QPoint(round(frame_obj.x()), round(frame_obj.y() / 3)))
            self.animation_1.setDuration(9500)
            self.animation_2 = QPropertyAnimation(frame_obj, b'pos')
            self.animation_2.setEndValue(QPoint(round(frame_obj.x()), round(frame_obj.y())))
            self.animation_2.setDuration(500)
            self.anim_group = QSequentialAnimationGroup()
            self.anim_group.addAnimation(self.animation_1)
            self.anim_group.addAnimation(self.animation_2)
            self.anim_group.start()
        elif cmd == 'neutral':
            print('neutral training')

    def get_user_prof(self):
        with open("user.json", "r") as user_file:
            user_info = json.load(user_file)
        user = {
            "license": user_info["license"],
            "client_id": user_info["client_id"],
            "client_secret": user_info["client_secret"],
            "debit": user_info["debit"]
        }
        return user

    def CreateProfile(self):
        headset_stat = check_headset_connection(self.user)
        self.ProfileLine.setStyleSheet("color:white;")
        if headset_stat:
            self.toggle_training_btn('train')
            self.t = Train(self.get_user_prof())
            self.t.accept_signal.connect(self.t.accept_training)
            self.t.reject_signal.connect(self.t.reject_training)
            self.t.delete_signal.connect(self.t.delete_training)
            self.t.do_prepare_steps()
            self.t.subscribe_data(['sys'])
            self.profile_name = self.ProfileLine.text()
            self.t.load_profile(self.profile_name)

            if self.t.get_trained_data(self.profile_name):
                temp = self.t.get_trained_data(self.profile_name)
                for entry in temp:
                    if entry['action'] == 'neutral':
                        self.NeutralLabel.setText(str(entry['times']))
                        self.NeutralLabelCounter += entry['times']
                    elif entry['action'] == 'push':
                        self.PushLabel.setText(str(entry['times']))
                        self.PushLabelCounter += entry['times']
                    elif entry['action'] == 'pull':
                        self.PullLabel.setText(str(entry['times']))
                        self.PullLabelCounter += entry['times']
                    elif entry['action'] == 'lift':
                        self.LiftLabel.setText(str(entry['times']))
                        self.LiftLabelCounter += entry['times']
                    elif entry['action'] == 'drop':
                        self.DropLabel.setText(str(entry['times']))
                        self.DropLabelCounter += entry['times']
            self.profile_name = (self.ProfileLine.text())
        else:
            self.ProfileLine.setText(
                "No headsets found. connect your headset using Emotiv app, change this profile name and try again")
            self.ProfileLine.setStyleSheet("color:red;")

    def plot_brain_map(self):
        map_data = brain_map(self.get_user_prof(), self.profile_name)
        if map_data:
            x = []
            y = []
            for entry in map_data:
                x.append(entry['coordinates'][0])
                y.append(entry['coordinates'][1])
            self.plot(x, y)

    def plot(self, x, y):
        print('plotting ------------------------------')
        self.ax.clear()
        color_grid = ["red", "green", "blue", "yellow", "purple"]
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_facecolor("grey")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for i in range(len(x)):
            self.ax.scatter(x[i], y[i], color=color_grid[i], zorder=5)
        self.canvas.draw()  # Refresh the canvas to display the graph

    def accept_training(self, action):
        print('accepted training')
        self.AccBtn.hide()
        self.RejBtn.hide()
        self.t.accept_signal.emit(self.profile_name, action)

    def reject_training(self, action):
        print('rejected training')
        self.AccBtn.hide()
        self.RejBtn.hide()
        self.t.reject_signal.emit(self.profile_name, action)

    def delete_training(self, action):
        print('deleted training')
        self.AccBtn.hide()
        self.RejBtn.hide()
        self.t.delete_signal.emit(self.profile_name, action)

    def update_counter_label(self, cmd):
        if cmd == 'neutral':
            self.NeutralLabelCounter += 1
            self.NeutralLabel.setText(str(self.NeutralLabelCounter))
            self.current_cmd = 'neutral'
        elif cmd == 'push':
            self.PushLabelCounter += 1
            self.PushLabel.setText(str(self.PushLabelCounter))
            self.current_cmd = 'push'
        elif cmd == 'pull':
            self.PullLabelCounter += 1
            self.PullLabel.setText(str(self.PullLabelCounter))
            self.current_cmd = 'pull'
        elif cmd == 'lift':
            self.LiftLabelCounter += 1
            self.LiftLabel.setText(str(self.LiftLabelCounter))
            self.current_cmd = 'lift'
        elif cmd == 'drop':
            self.DropLabelCounter += 1
            self.DropLabel.setText(str(self.DropLabelCounter))
            self.current_cmd = 'drop'
        elif cmd == 'neutral-delete':
            self.NeutralLabelCounter = 0
            self.NeutralLabel.setText(str(self.NeutralLabelCounter))
        elif cmd == 'push-delete':
            self.PushLabelCounter = 0
            self.PushLabel.setText(str(self.PushLabelCounter))
        elif cmd == 'pull-delete':
            self.PullLabelCounter = 0
            self.PullLabel.setText(str(self.PullLabelCounter))
        elif cmd == 'lift-delete':
            self.LiftLabelCounter = 0
            self.LiftLabel.setText(str(self.LiftLabelCounter))
            self.current_cmd = 'lift'
        elif cmd == 'drop-delete':
            self.DropLabelCounter = 0
            self.DropLabel.setText(str(self.DropLabelCounter))

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
        self.wheelchair.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.training.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        self.spotify.setStyleSheet(
            "text-align:left;border:none;padding: 2px 5px;color:white;margin:0;background-color:transparent;")
        if tab == 'keyboard':
            self.keyboard.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'smart':
            self.smarthome.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'TrainingPage':
            self.training.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'spotify':
            self.spotify.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'fes':
            self.fes.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'other':
            self.other.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'wheelchair':
            self.wheelchair.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'settings':
            self.settings.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'help':
            self.hlp.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")

    def set_headset_status(self):
        stat = check_headset_connection(self.user)
        if stat:
            self.keyHeadLabel.setText("Emotiv headset is connected!")
            self.smartHeadLabel.setText("Emotiv headset is connected!")
            self.fesHeadLabel.setText("Emotiv headset is connected!")
            self.WCHeadLabel.setText("Emotiv headset is connected!")
            self.spotifyHeadLabel.setText("Emotiv headset is connected!")
            self.keyHeadLabel.setStyleSheet("color:white;")
            self.smartHeadLabel.setStyleSheet("color:white;")
            self.fesHeadLabel.setStyleSheet("color:white;")
            self.WCHeadLabel.setStyleSheet("color:white;")
            self.spotifyHeadLabel.setStyleSheet("color:white;")
        else:
            self.keyHeadLabel.setText("Emotiv headset is NOT connected!")
            self.smartHeadLabel.setText("Emotiv headset is NOT connected!")
            self.fesHeadLabel.setText("Emotiv headset is NOT connected!")
            self.WCHeadLabel.setText("Emotiv headset is NOT connected!")
            self.spotifyHeadLabel.setText("Emotiv headset is NOT connected!")
            self.keyHeadLabel.setStyleSheet("color:red;")
            self.smartHeadLabel.setStyleSheet("color:red;")
            self.fesHeadLabel.setStyleSheet("color:red;")
            self.WCHeadLabel.setStyleSheet("color:red;")
            self.spotifyHeadLabel.setStyleSheet("color:red;")

    def set_arduino_status(self):

        arduino_Stat = check_arduino_connection()
        if arduino_Stat:
            self.fesStatLabel.setText("Hub box is connected!")
            self.WCStatLabel.setText("Hub box is connected!")
            self.fesStatLabel.setStyleSheet("color:white;")
            self.WCStatLabel.setStyleSheet("color:white;")

        else:
            self.fesStatLabel.setText("Hub box is NOT connected!")
            self.WCStatLabel.setText("Hub box is NOT connected!")
            self.fesStatLabel.setStyleSheet("color:red;")
            self.WCStatLabel.setStyleSheet("color:red;")

    def headset_thread(self):

        # arduino_serial = self.ArduinoSerial
        # threshold = self.activation_threshold
        # dly = self.activation_delay
        # min_dly = self.fes_min_dly
        key = [self.key_push, self.key_pull, self.key_lift, self.key_drop]
        triggers = [self.fes_on, self.fes_off]
        device_ip = [self.dev1_ip, self.dev2_ip]
        device_act = [self.dev1_act, self.dev2_act]
        device_duration = self.smart_on_period
        btn_action = [self.btn_1, self.btn_2, self.btn_3, self.btn_4]
        spotify_cmd = [self.spot_play, self.spot_pause, self.spot_next, self.spot_prev, self.spot_min_dly]

        # while True:
        try:
            self.set_headset_status()
            c = Cortex(self.user, debug_mode=False)
            t = train.Train(self.user)
            c.bind(new_com_data=t.on_new_data)
            c.do_prepare_steps()
            c.sub_request(['sys'])
            stream = ['com']
            status = 'load'
            c.setup_profile(self.profile_name, status)
            prev = 'off'
            prev_wc_btn = 'off'
            prev_time = 0
            while True:
                prev, last_act, prev_wc_btn, data, prev_time = c.sub_request_GRH(stream, self.activation_threshold, self.activation_delay, [self.key_push, self.key_pull, self.key_lift, self.key_drop],
                                                                                 self.ArduinoSerial, [self.fes_on, self.fes_off],
                                                                                 self.fes_min_dly, self.flag, self.environment,
                                                                                 prev, [self.dev1_ip, self.dev2_ip], [self.dev1_act, self.dev2_act],
                                                                                 self.smart_on_period, prev_wc_btn,
                                                                                 [self.btn_1, self.btn_2, self.btn_3, self.btn_4], [self.spot_play, self.spot_pause, self.spot_next, self.spot_prev, self.spot_min_dly], prev_time,
                                                                                 self.latch_flag)
                if last_act:
                    activations.append(last_act)

                self.update_signal.emit(data)
                # self.update_progress_bar(data)
        except:
            print("No headset connected!")
            # self.flag = "-"

    def start_thread(self, env, profile):
        self.environment = env
        if self.flag == "-":
            self.thread.run = self.headset_thread
            self.thread.start()
            # send_thread = threading.Thread(target=self.headset_thread, args=[ArduinoSerial, profile], daemon=True)
            self.flag = 'go'
            # send_thread.start()
            self.toggle_training_btn('started')
        else:
            self.flag = 'go'
            self.toggle_training_btn('started')

    def stop_thread(self):
        self.flag = 'stop'
        self.toggle_training_btn('paused')

    def update_progress_bar(self, data):
        if data[0] == "push":
            self.keyLabel.setStyleSheet("color:green;")
            self.smartLabel.setStyleSheet("color:green;")
            self.fesLabel.setStyleSheet("color:green;")
            self.spotifyLabel.setStyleSheet("color:green;")
            self.WCLabel.setStyleSheet("color:green;")
        elif data[0] == "pull":
            self.keyLabel.setStyleSheet("color:blue;")
            self.smartLabel.setStyleSheet("color:blue;")
            self.fesLabel.setStyleSheet("color:blue;")
            self.spotifyLabel.setStyleSheet("color:blue;")
            self.WCLabel.setStyleSheet("color:blue;")
        elif data[0] == "lift":
            self.keyLabel.setStyleSheet("color:yellow;")
            self.smartLabel.setStyleSheet("color:yellow;")
            self.fesLabel.setStyleSheet("color:yellow;")
            self.spotifyLabel.setStyleSheet("color:yellow;")
            self.WCLabel.setStyleSheet("color:yellow;")
        elif data[0] == "drop":
            self.keyLabel.setStyleSheet("color:purple;")
            self.smartLabel.setStyleSheet("color:purple;")
            self.fesLabel.setStyleSheet("color:purple;")
            self.spotifyLabel.setStyleSheet("color:purple;")
            self.WCLabel.setStyleSheet("color:purple;")
        else:
            self.keyLabel.setStyleSheet("color:white;")
            self.smartLabel.setStyleSheet("color:white;")
            self.fesLabel.setStyleSheet("color:white;")
            self.spotifyLabel.setStyleSheet("color:white;")
            self.WCLabel.setStyleSheet("color:white;")

        self.keyLabel.setText("Mental command: " + (data[0] + "\n" + "Power:  " + str(int(100 * data[1]))) + "/100")
        self.smartLabel.setText("Mental command: " + (data[0] + "\n" + "Power:  " + str(int(100 * data[1]))) + "/100")
        self.fesLabel.setText("Mental command: " + (data[0] + "\n" + "Power:  " + str(int(100 * data[1]))) + "/100")
        self.spotifyLabel.setText("Mental command: " + (data[0] + "\n" + "Power:  " + str(int(100 * data[1]))) + "/100")
        self.WCLabel.setText("Mental command: " + (data[0] + "\n" + "Power:  " + str(int(100 * data[1]))) + "/100")


"""
 headset_thread: a thread that generates an object from the Emotiv cortex  class and 
 runs the sub_request_GRH function in an infinite while loop. this function constantly 
 reads data generated by the heads1111et and maps it to keyboard key presses, FES, or smartplug outputs. 
"""

'''
    set_target: is the function that is used in target_recording_thread to record external button presses. these presses 
    indicate targets generated by the third-party for BCI user to activate the BCI paradigm. these targets and their 
    following activations are used to generate a report in csv format in the data_sets folder in project path. 
'''


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


# generating main window object
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setWindowIcon(QtGui.QIcon("logo.png"))
widget.setWindowTitle("GRH Home-BCI")
widget.show()

# starting target recording thread
target_recording_thread = threading.Thread(target=set_target, args=(), daemon=True)
target_recording_thread.start()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
