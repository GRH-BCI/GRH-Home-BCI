import sys
import PyQt5
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtCore
import select
import threading
import json
from utils import *
from PyQt5.QtCore import QThread, pyqtSignal, QRect, QPropertyAnimation, QThreadPool, QRunnable
from PIL import Image
import matplotlib.pyplot as plt
import queue
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QFrame
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
import time
import resources_rc
import atexit

global activations, targets

activations = []
targets = []


class WelcomeScreen(QDialog):
    update_signal = pyqtSignal(list)

    class Worker(QRunnable):
        """Worker thread that runs a given function in a separate thread."""

        def __init__(self, parent, function):
            super().__init__()
            self.parent = parent  # Reference to MyApp instance
            self.function = function  # Function to execute
            self.setAutoDelete(True)  # Ensures proper cleanup

        @pyqtSlot()
        def run(self):
            """Execute the assigned function."""
            self.function()

    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.profile_name = ''
        self.time_left_int = 10
        self.stackedWidget.setCurrentIndex(0)
        self.myTimer = QtCore.QTimer(self)
        self.flag = "-"
        self.environment = 'TrainingPage'
        self.frozen = '-'
        self.freezeable = '-'
        self.freezeFlag = False
        self.AT_sock = None
        self.latch_flag = [False, False, False, False, True]
        self.BCISW = False
        self.BCIOnly.setChecked(True)
        self.BCIandSw.setChecked(False)
        self.threadpool = QThreadPool()

        # self.menu.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.training.clicked.connect(
            lambda: [self.stackedWidget.setCurrentIndex(0), self.update_borders('TrainingPage')])
        self.keyboard.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(1), self.update_borders('keyboard')])
        self.smarthome.clicked.connect(lambda: [self.stackedWidget.setCurrentIndex(2), self.update_borders('smart-home')])
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
            lambda: [self.resize_animation('neutral'), self.train_mental('neutral'),
                     self.toggle_training_btn('training'),
                     self.update_counter_label('neutral'), self.startTimer()])
        self.PushTrn.clicked.connect(
            lambda: [self.resize_animation('push'), self.train_mental('push'), self.toggle_training_btn('training'),
                     self.update_counter_label('push'), self.startTimer()])
        self.PullTrn.clicked.connect(
            lambda: [self.resize_animation('pull'), self.train_mental('pull'), self.toggle_training_btn('training'),
                     self.update_counter_label('pull'), self.startTimer()])
        self.LiftTrn.clicked.connect(
            lambda: [self.resize_animation('lift'), self.train_mental('lift'), self.toggle_training_btn('training'),
                     self.update_counter_label('lift'), self.startTimer()])
        self.DropTrn.clicked.connect(
            lambda: [self.resize_animation('drop'), self.train_mental('drop'), self.toggle_training_btn('training'),
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
        self.fesCheckBtn.clicked.connect(lambda: self.connect_AT_hub())
        self.fesStartBtn.clicked.connect(lambda: self.start_thread("fes", self.profile_name))
        self.fesPauseBtn.clicked.connect(lambda: self.stop_thread())
        self.fesManualOnBtn.clicked.connect(lambda: manual_start(self.AT_sock))
        self.fesManualOffBtn.clicked.connect(lambda: manual_stop(self.AT_sock))
        # self.fesReportBtn.clicked.connect(lambda: generate_report(success_threshold, activations, targets))

        # other page
        self.paintLaunchBtn.clicked.connect(lambda: launch_app("BCI Paint"))
        self.gamingLaunchBtn.clicked.connect(lambda: launch_app("BCI Gaming"))

        # wheelchair page
        self.WCCheckBtn.clicked.connect(lambda: self.connect_AT_hub())
        self.WCStartBtn.clicked.connect(lambda: self.start_thread("wc", self.profile_name))
        self.WCPauseBtn.clicked.connect(lambda: self.stop_thread())
        self.WCCheckBtn.clicked.connect(lambda: self.set_headset_status())

        self.WCManualOnBtn_1.pressed.connect(lambda: manual_btn_control(self.AT_sock, 11))
        self.WCManualOnBtn_1.released.connect(lambda: manual_btn_control(self.AT_sock, 10))
        self.WCManualOnBtn_2.pressed.connect(lambda: manual_btn_control(self.AT_sock, 21))
        self.WCManualOnBtn_2.released.connect(lambda: manual_btn_control(self.AT_sock, 20))
        self.WCManualOnBtn_3.pressed.connect(lambda: manual_btn_control(self.AT_sock, 31))
        self.WCManualOnBtn_3.released.connect(lambda: manual_btn_control(self.AT_sock, 30))
        self.WCManualOnBtn_4.pressed.connect(lambda: manual_btn_control(self.AT_sock, 41))
        self.WCManualOnBtn_4.released.connect(lambda: manual_btn_control(self.AT_sock, 40))

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
        self.LatchBtn1.clicked.connect(lambda: self.latch_mode(1))
        self.LatchBtn2.clicked.connect(lambda: self.latch_mode(2))
        self.LatchBtn3.clicked.connect(lambda: self.latch_mode(3))
        self.LatchBtn4.clicked.connect(lambda: self.latch_mode(4))
        self.BCIOnly.clicked.connect(lambda: self.latch_mode(5))
        self.BCIandSw.clicked.connect(lambda: self.latch_mode(6))

        # help page
        self.openManualBtn.clicked.connect(lambda: launch_app("manual"))

        # update ui preset values
        self.set_ui_parameters()
        self.set_headset_status()
        self.thread = QThread()
        self.update_signal.connect(self.update_progress_bar)
        self.q_train = queue.Queue()

    def train_mental(self, training_action):
        train_thread = threading.Thread(target=self.t.train_mc, args=(training_action, self.q_train))
        train_thread.start()

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
        self.fes_acceptable_dly = config["fes_acceptable_dly"]
        self.fes_min_dly = config["fes_min_dly"]
        self.AT_name = config["hub_name"]
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
        self.s1 = config["s1"]
        self.s2 = config["s2"]
        self.s3 = config["s3"]
        self.s4 = config["s4"]
        self.s1D = config["s1D"]
        self.s2D = config["s2D"]
        self.s3D = config["s3D"]
        self.s4D = config["s4D"]
        self.wcPush = config["pushSW"]
        self.wcPull = config["pullSW"]
        self.wcLift = config["liftSW"]
        self.wcDrop = config["dropSW"]

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
        drc_mapping = ['-', 'forward', 'backward', 'left', 'right']
        switch_mapping = ["-", "Drive", "Freeze&Drive", "Freeze/Unfreeze", "Out1", "Out2", "Out3", "Out4", "Out5", "Start",
                          "Pause"]
        switch_double_mapping = ["-", "Freeze/Unfreeze", "Start", "Pause"]
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
        self.ComPortLine.setText(str(self.AT_name))
        self.trgtActDlySpin.setValue(int(self.fes_acceptable_dly))
        self.minDlySpin.setValue(int(self.fes_min_dly))
        self.smartSpinBox.setValue(int(self.smart_on_period))
        self.wcCombo_1.setCurrentIndex(emotiv_cmnds.index(self.btn_1))
        self.wcCombo_2.setCurrentIndex(emotiv_cmnds.index(self.btn_2))
        self.wcCombo_3.setCurrentIndex(emotiv_cmnds.index(self.btn_3))
        self.wcCombo_4.setCurrentIndex(emotiv_cmnds.index(self.btn_4))
        self.S1Combo.setCurrentIndex(switch_mapping.index(self.s1))
        self.S2Combo.setCurrentIndex(switch_mapping.index(self.s2))
        self.S3Combo.setCurrentIndex(switch_mapping.index(self.s3))
        self.S4Combo.setCurrentIndex(switch_mapping.index(self.s4))
        self.S1DCombo.setCurrentIndex(switch_double_mapping.index(self.s1D))
        self.S2DCombo.setCurrentIndex(switch_double_mapping.index(self.s2D))
        self.S3DCombo.setCurrentIndex(switch_double_mapping.index(self.s3D))
        self.S4DCombo.setCurrentIndex(switch_double_mapping.index(self.s4D))
        self.wcPushCombo.setCurrentIndex(drc_mapping.index(self.wcPush))
        self.wcPullCombo.setCurrentIndex(drc_mapping.index(self.wcPull))
        self.wcLiftCombo.setCurrentIndex(drc_mapping.index(self.wcLift))
        self.wcDropCombo.setCurrentIndex(drc_mapping.index(self.wcDrop))
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
        drc_mapping = ['-', 'forward', 'backward', 'left', 'right']
        switch_mapping = ["-", "Drive", "Freeze&Drive", "Freeze/Unfreeze", "Out1", "Out2", "Out3", "Out4", "Out5", "Start",
                          "Pause"]
        switch_double_mapping = ["-", "Freeze/Unfreeze", "Start", "Pause"]
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
        config["hub_name"] = self.ComPortLine.text()
        config["s1"] = switch_mapping[self.S1Combo.currentIndex()]
        config["s2"] = switch_mapping[self.S2Combo.currentIndex()]
        config["s3"] = switch_mapping[self.S3Combo.currentIndex()]
        config["s4"] = switch_mapping[self.S4Combo.currentIndex()]
        config["s1D"] = switch_double_mapping[self.S1DCombo.currentIndex()]
        config["s2D"] = switch_double_mapping[self.S2DCombo.currentIndex()]
        config["s3D"] = switch_double_mapping[self.S3DCombo.currentIndex()]
        config["s4D"] = switch_double_mapping[self.S4DCombo.currentIndex()]
        config["pushSW"] = drc_mapping[self.wcPushCombo.currentIndex()]
        config["pullSW"] = drc_mapping[self.wcPullCombo.currentIndex()]
        config["liftSW"] = drc_mapping[self.wcLiftCombo.currentIndex()]
        config["dropSW"] = drc_mapping[self.wcDropCombo.currentIndex()]

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
        self.s1 = config["s1"]
        self.s2 = config["s2"]
        self.s3 = config["s3"]
        self.s4 = config["s4"]
        self.s1D = config["s1D"]
        self.s2D = config["s2D"]
        self.s3D = config["s3D"]
        self.s4D = config["s4D"]
        self.wcPush = config["pushSW"]
        self.wcPull = config["pullSW"]
        self.wcLift = config["liftSW"]
        self.wcDrop = config["dropSW"]

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
            self.fesManualOnBtn.setDisabled(True)
            self.fesManualOffBtn.setDisabled(True)
            self.WCManualOnBtn_1.setDisabled(True)
            self.WCManualOnBtn_2.setDisabled(True)
            self.WCManualOnBtn_3.setDisabled(True)
            self.WCManualOnBtn_4.setDisabled(True)
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

        elif BtnNum == 5:
            if self.BCIOnly.isChecked():
                self.BCISW = False
                self.BCIandSw.setChecked(False)
                self.latch_flag[4] = False
            else:
                self.BCISW = True
                self.BCIandSw.setChecked(True)
                self.latch_flag[4] = True

        elif BtnNum == 6:
            if self.BCIandSw.isChecked():
                self.BCISW = True
                self.BCIOnly.setChecked(False)
                self.latch_flag[4] = True

            else:
                self.BCISW = False
                self.BCIOnly.setChecked(True)
                self.latch_flag[4] = False
        print(self.latch_flag)


    def openImagePopUp(self):
        path = QFileDialog.getOpenFileNames(self, 'Choose mental image object:', '.\\Assets', "Image files (*.png)")
        if path[0]:
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
            temp = str(self.q_train.get())
            print(temp)
            if temp == "MC_Failed":
                print('rejected due to low quality')
                warningMsg = QMessageBox()
                warningMsg.setWindowTitle("Oops..!")
                warningMsg.setText("Contact quality is below 50%. please, adjust the headset to reach higher contact "
                                   "quality and try again.")
                warningMsg.exec_()
                self.toggle_training_btn('train')
                self.update_counter_label(str(self.current_cmd + "-1"))
            else:
                self.AccBtn.show()
                self.RejBtn.show()
            self.myTimer.stop()
            self.myTimer.timeout.disconnect(self.timerTimeout)

        self.timerLabel.setText(str(self.time_left_int))

    def btnstate(self):
        if self.WCManualOnBtn_1.isChecked():
            manual_btn_control(self.AT_sock, 1)
        else:
            manual_btn_control(self.AT_sock, 0)
        if self.WCManualOnBtn_2.isChecked():
            manual_btn_control(self.AT_sock, 2)
        else:
            manual_btn_control(self.AT_sock, 0)
        if self.WCManualOnBtn_3.isChecked():
            manual_btn_control(self.AT_sock, 3)
        else:
            manual_btn_control(self.AT_sock, 0)
        if self.WCManualOnBtn_4.isChecked():
            manual_btn_control(self.AT_sock, 4)
        else:
            manual_btn_control(self.AT_sock, 0)

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
        self.update_counter_label(str(action + "-1"))

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

        elif cmd == 'neutral-1':
            self.NeutralLabelCounter -= 1
            self.NeutralLabel.setText(str(self.NeutralLabelCounter))
            self.current_cmd = 'neutral'
        elif cmd == 'push-1':
            self.PushLabelCounter -= 1
            self.PushLabel.setText(str(self.PushLabelCounter))
            self.current_cmd = 'push'
        elif cmd == 'pull-1':
            self.PullLabelCounter -= 1
            self.PullLabel.setText(str(self.PullLabelCounter))
            self.current_cmd = 'pull'
        elif cmd == 'lift-1':
            self.LiftLabelCounter -= 1
            self.LiftLabel.setText(str(self.LiftLabelCounter))
            self.current_cmd = 'lift'
        elif cmd == 'drop-1':
            self.DropLabelCounter += 1
            self.DropLabel.setText(str(self.DropLabelCounter))
            self.current_cmd = 'drop'

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
            self.environment = 'keyboard'
        elif tab == 'smart-home':
            self.environment = 'smart'
            self.smarthome.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'TrainingPage':
            self.environment = 'training'
            self.training.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'spotify':
            self.environment = 'spotify'
            self.spotify.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'fes':
            self.environment = 'fes'
            self.fes.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'other':
            self.other.setStyleSheet(
                "text-align:left;border:none;padding: 2px 5px;border-top : 3px solid rgb(93, 88, 255);border-bottom: 3px solid rgb(93, 88, 255);color:rgb(93, 88, 255);margin:0;background-color:transparent;")
        elif tab == 'wheelchair':
            self.environment = 'wc'
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

    def connect_AT_hub(self):
        with open("config.json", "r") as config_File:
            config = json.load(config_File)
        blth_name = config['hub_name']
        try:
            self.AT_mac = find_blth_ports(blth_name)
            self.AT_sock = connect_to_blth(self.AT_mac)
            if self.AT_sock:
                self.fesStatLabel.setText("AT_Hub is connected!")
                self.WCStatLabel.setText("AT_Hub is connected!")
                self.fesStatLabel.setStyleSheet("color:white;")
                self.WCStatLabel.setStyleSheet("color:white;")

                self.fesManualOnBtn.setDisabled(False)
                self.fesManualOffBtn.setDisabled(False)
                self.WCManualOnBtn_1.setDisabled(False)
                self.WCManualOnBtn_2.setDisabled(False)
                self.WCManualOnBtn_3.setDisabled(False)
                self.WCManualOnBtn_4.setDisabled(False)
            else:
                self.fesStatLabel.setText("AT_Hub is NOT connected!")
                self.WCStatLabel.setText("AT_Hub is NOT connected!")
                self.fesStatLabel.setStyleSheet("color:red;")
                self.WCStatLabel.setStyleSheet("color:red;")
                self.fesManualOnBtn.setDisabled(True)
                self.fesManualOffBtn.setDisabled(True)
                self.WCManualOnBtn_1.setDisabled(True)
                self.WCManualOnBtn_2.setDisabled(True)
                self.WCManualOnBtn_3.setDisabled(True)
                self.WCManualOnBtn_4.setDisabled(True)


        except Exception as e:
            QMessageBox.warning(self, "Warning", f"no AT-hub with name {blth_name} could be reached")
            self.fesManualOnBtn.setDisabled(True)
            self.fesManualOffBtn.setDisabled(True)
            self.WCManualOnBtn_1.setDisabled(True)
            self.WCManualOnBtn_2.setDisabled(True)
            self.WCManualOnBtn_3.setDisabled(True)
            self.WCManualOnBtn_4.setDisabled(True)

    def headset_thread(self):

        print("headset thread started")
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
                prev, last_act, prev_wc_btn, data, prev_time = c.sub_request_GRH(stream, self.activation_threshold,
                                                                                 self.activation_delay,
                                                                                 [self.key_push, self.key_pull,
                                                                                  self.key_lift, self.key_drop],
                                                                                 self.AT_sock,
                                                                                 [self.fes_on, self.fes_off],
                                                                                 self.fes_min_dly, self.flag,
                                                                                 self.environment,
                                                                                 prev, [self.dev1_ip, self.dev2_ip],
                                                                                 [self.dev1_act, self.dev2_act],
                                                                                 self.smart_on_period, prev_wc_btn,
                                                                                 [self.btn_1, self.btn_2, self.btn_3,
                                                                                  self.btn_4],
                                                                                 [self.spot_play, self.spot_pause,
                                                                                  self.spot_next, self.spot_prev,
                                                                                  self.spot_min_dly], prev_time,
                                                                                 self.latch_flag)
                if last_act:
                    activations.append(last_act)

                self.update_signal.emit(data)
                # self.update_progress_bar(data)
        except:
            print("No headset connected!")
            # self.flag = "-"

    def input_thread(self):
        print("input thread started")
        if self.AT_sock:
            message = False
            while True:
                ready, _, _ = select.select([self.AT_sock], [], [], 0.1)  # Timeout of 0.1 seconds
                # Checking if there is data being recieved from the arduino.
                if ready:
                    # Read the data and decode it from binary to ascii
                    message = blth_handler.receive_data(self.AT_sock)

                    # possible values for message are
                    # 'DTB'(and then a number from 1-6), Double Tap Button
                    # 'TB'(and then a number from 1-6), Tap Button
                    # 'LGB'(and then a number from 1-6), Let Go Button
                    # 'HB'(and then a number from 1-6) Hold Button
                    match message:
                        case "TB1":
                            self.switch_handler(self.AT_sock, self.s1, 'tap')
                        case "TB2":
                            self.switch_handler(self.AT_sock, self.s2, 'tap')
                        case "TB3":
                            self.switch_handler(self.AT_sock, self.s3, 'tap')
                        case "TB4":
                            self.switch_handler(self.AT_sock, self.s4, 'tap')
                        # case "TB5":
                        #     self.switch_handler(self.AT_sock, self.s5, 'tap')
                        case "HB1":
                            self.switch_handler(self.AT_sock, self.s1, 'hold')
                        case "HB2":
                            self.switch_handler(self.AT_sock, self.s2, 'hold')
                        case "HB3":
                            self.switch_handler(self.AT_sock, self.s3, 'hold')
                        case "HB4":
                            self.switch_handler(self.AT_sock, self.s4, 'hold')
                        # case "HB5":
                        #     self.switch_handler(self.AT_sock, self.s5, 'hold')
                        case "LGB1":
                            self.switch_handler(self.AT_sock, self.s1, 'release')
                        case "LGB2":
                            self.switch_handler(self.AT_sock, self.s2, 'release')
                        case "LGB3":
                            self.switch_handler(self.AT_sock, self.s3, 'release')
                        case "LGB4":
                            self.switch_handler(self.AT_sock, self.s4, 'release')
                        # case "LGB5":
                        #     self.switch_handler(self.AT_sock, self.s5, 'release')
                        case "DTB1":
                            self.switch_handler(self.AT_sock, self.s1D, 'double')
                        case "DTB2":
                            self.switch_handler(self.AT_sock, self.s2D, 'double')
                        case "DTB3":
                            self.switch_handler(self.AT_sock, self.s3D, 'double')
                        case "DTB4":
                            self.switch_handler(self.AT_sock, self.s4D, 'double')
        else:
            print("no AT hub")

    def switch_handler(self, sock, cmd, type):
        tap_duration = 0.05
        freezetags = ['-', 'forward', 'backward', 'left', 'right']
        if self.BCISW:
            if type == 'tap':
                match cmd:
                    case 'Out1':
                        blth_handler.send_data(sock, 'R11')
                        time.sleep(tap_duration)
                        blth_handler.send_data(sock, 'R10')
                    case 'Out2':
                        blth_handler.send_data(sock, 'R21')
                        time.sleep(tap_duration)
                        blth_handler.send_data(sock, 'R20')
                    case 'Out3':
                        blth_handler.send_data(sock, 'R31')
                        time.sleep(tap_duration)
                        blth_handler.send_data(sock, 'R30')
                    case 'Out4':
                        blth_handler.send_data(sock, 'R41')
                        time.sleep(tap_duration)
                        blth_handler.send_data(sock, 'R40')
                    case 'Out5':
                        blth_handler.send_data(sock, 'R51')
                        time.sleep(tap_duration)
                        blth_handler.send_data(sock, 'R50')
                    case 'Feeze&Drive':
                        if self.freezeFlag:
                            self.freezeFlag = False
                            self.WCFrozenLabel.setText("Frozen command: " + "--")
                            self.frozen = '-'
                        else:
                            self.freezeFlag = True
                            self.frozen = self.freezeable
                            self.WCFrozenLabel.setText("Frozen command: " + self.frozen)
                            button_number = freezetags.index(self.frozen)
                            if button_number != 0:
                                blth_handler.send_data(sock, f'R{button_number}1')
                                time.sleep(tap_duration)
                                blth_handler.send_data(sock, f'R{button_number}0')
                    case 'Freeze/Unfreeze':
                        if self.freezeFlag:
                            self.freezeFlag = False
                            self.WCFrozenLabel.setText("Frozen command: " + "--")
                            self.frozen = '-'
                        else:
                            self.freezeFlag = True
                            self.frozen = self.freezeable
                            self.WCFrozenLabel.setText("Frozen command: " + self.frozen)
                    case 'Drive':
                        if self.frozen != '-':
                            button_number = freezetags.index(self.frozen)
                            blth_handler.send_data(sock, f'R{button_number}1')
                            time.sleep(tap_duration)
                            blth_handler.send_data(sock, f'R{button_number}0')
                    case 'Start':
                        self.start_thread(self.environment, self.profile_name)
                    case 'Pause':
                        self.stop_thread()
            elif type == 'hold':
                match cmd:
                    case 'Out1':
                        blth_handler.send_data(sock, 'R11')
                    case 'Out2':
                        blth_handler.send_data(sock, 'R21')
                    case 'Out3':
                        blth_handler.send_data(sock, 'R31')
                    case 'Out4':
                        blth_handler.send_data(sock, 'R41')
                    case 'Out5':
                        blth_handler.send_data(sock, 'R51')
                    case 'Feeze&Drive':
                        self.freezeFlag = True
                        self.frozen = self.freezeable
                        self.WCFrozenLabel.setText("Frozen command: " + self.frozen)
                        button_number = freezetags.index(self.frozen)
                        if button_number != 0:
                            blth_handler.send_data(sock, f'R{button_number}1')
                    case 'Freeze/Unfreeze':
                        if self.freezeFlag:
                            self.freezeFlag = False
                            self.WCFrozenLabel.setText("Frozen command: " + "--")
                            self.frozen = '-'
                        else:
                            self.freezeFlag = True
                            self.frozen = self.freezeable
                            self.WCFrozenLabel.setText("Frozen command: " + self.frozen)
                    case 'Drive':
                        if self.frozen != '-':
                            button_number = freezetags.index(self.frozen)
                            blth_handler.send_data(sock, f'R{button_number}1')
            elif type == 'release':
                match cmd:
                    case 'Out1':
                        blth_handler.send_data(sock, 'R10')
                    case 'Out2':
                        blth_handler.send_data(sock, 'R20')
                    case 'Out3':
                        blth_handler.send_data(sock, 'R30')
                    case 'Out4':
                        blth_handler.send_data(sock, 'R40')
                    case 'Out5':
                        blth_handler.send_data(sock, 'R50')
                    case 'Feeze&Drive':
                        self.freezeFlag = False
                        button_number = freezetags.index(self.frozen)
                        self.frozen = '-'
                        self.WCFrozenLabel.setText("Frozen command: " + '-')
                        if button_number != 0:
                            blth_handler.send_data(sock, f'R{button_number}0')
                    case 'Freeze/Unfreeze':
                        print('released')
                    case 'Drive':
                        if self.frozen != '-':
                            button_number = freezetags.index(self.frozen)
                            blth_handler.send_data(sock, f'R{button_number}0')
                    case 'Start':
                        self.start_thread("wc", self.profile_name)
                    case 'Pause':
                        self.stop_thread()
            elif type == 'double':
                print(self.freezeFlag)
                print(self.freezeable)
                print(self.frozen)
                match cmd:
                    case 'Freeze/Unfreeze':
                        print(self.freezeFlag)
                        if self.freezeFlag:
                            self.freezeFlag = False
                            self.WCFrozenLabel.setText("Unfrozen")
                            self.frozen = '-'
                        else:
                            self.freezeFlag = True
                            self.frozen = self.freezeable
                            self.WCFrozenLabel.setText("Frozen command: " + self.frozen)
                    case 'Start':
                        self.start_thread("wc", self.profile_name)
                    case 'Pause':
                        self.stop_thread()

    def start_thread(self, env, profile):
        self.environment = env
        if self.flag == "-":
            worker1 = self.Worker(self, self.headset_thread)
            worker2 = self.Worker(self, self.input_thread)

            self.threadpool.start(worker1)
            self.threadpool.start(worker2)

            # self.thread.run = self.headset_thread
            # self.thread.start()
            self.flag = 'go'
            self.toggle_training_btn('started')
        else:
            self.flag = 'go'
            self.toggle_training_btn('started')

    def stop_thread(self):
        self.flag = 'stop'
        self.toggle_training_btn('paused')

    def update_progress_bar(self, data):

        freezetags = ['-', 'forward', 'backward', 'left', 'right']
        if data[0] == "push":
            self.keyLabel.setStyleSheet("color:green;")
            self.smartLabel.setStyleSheet("color:green;")
            self.fesLabel.setStyleSheet("color:green;")
            self.spotifyLabel.setStyleSheet("color:green;")
            self.WCLabel.setStyleSheet("color:green;")
            self.WCFrozenLabel.setStyleSheet("color:green;")
            if self.BCISW == True and 100*data[1] >= self.activation_threshold:
                self.freezeable = freezetags[self.wcPushCombo.currentIndex()]
            else:
                self.freezeable = '-'

        elif data[0] == "pull":
            self.keyLabel.setStyleSheet("color:blue;")
            self.smartLabel.setStyleSheet("color:blue;")
            self.fesLabel.setStyleSheet("color:blue;")
            self.spotifyLabel.setStyleSheet("color:blue;")
            self.WCLabel.setStyleSheet("color:blue;")
            self.WCFrozenLabel.setStyleSheet("color:blue;")
            if self.BCISW == True and 100*data[1] >= self.activation_threshold:
                self.freezeable = freezetags[self.wcPullCombo.currentIndex()]
            else:
                self.freezeable = '-'
        elif data[0] == "lift":
            self.keyLabel.setStyleSheet("color:yellow;")
            self.smartLabel.setStyleSheet("color:yellow;")
            self.fesLabel.setStyleSheet("color:yellow;")
            self.spotifyLabel.setStyleSheet("color:yellow;")
            self.WCLabel.setStyleSheet("color:yellow;")
            self.WCFrozenLabel.setStyleSheet("color:yellow;")
            if self.BCISW == True and 100*data[1] >= self.activation_threshold:
                self.freezeable = freezetags[self.wcLiftCombo.currentIndex()]
            else:
                self.freezeable = '-'
        elif data[0] == "drop":
            self.keyLabel.setStyleSheet("color:purple;")
            self.smartLabel.setStyleSheet("color:purple;")
            self.fesLabel.setStyleSheet("color:purple;")
            self.spotifyLabel.setStyleSheet("color:purple;")
            self.WCLabel.setStyleSheet("color:purple;")
            self.WCFrozenLabel.setStyleSheet("color:purple;")
            if self.BCISW == True and 100*data[1] >= self.activation_threshold:
                self.freezeable = freezetags[self.wcDropCombo.currentIndex()]
            else:
                self.freezeable = '-'
        else:
            self.keyLabel.setStyleSheet("color:white;")
            self.smartLabel.setStyleSheet("color:white;")
            self.fesLabel.setStyleSheet("color:white;")
            self.spotifyLabel.setStyleSheet("color:white;")
            self.WCLabel.setStyleSheet("color:white;")
            self.WCFrozenLabel.setStyleSheet("color:white;")
            self.freezeable = '-'

        print('in update phase' + self.freezeable)
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

#
# def set_target():
#     global targets, ArduinoSerial
#     try:
#         ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
#         ArduinoSerial.close()
#         ArduinoSerial.open()
#         print("arduino is conected")
#     except:
#         ArduinoSerial = False
#     while True:
#         '''
#             check if data is being received from arduino
#         '''
#         check = check_arduino_connection()
#         if check:
#             time.sleep(1)
#             try:
#                 message = ArduinoSerial.read()
#                 message = message.decode()
#                 if message == 'N':
#                     targets.append([1, time.time()])
#                 # Clearing the input buffer for serial
#                 if message == '2':
#                     targets.append([2, time.time()])
#                 if message == '3':
#                     targets.append([3, time.time()])
#                 if message == '4':
#                     targets.append([4, time.time()])
#                 if message == '5':
#                     targets.append([5, time.time()])
#                 time.sleep(1)
#
#                 ArduinoSerial.reset_input_buffer()
#
#             except:
#                 try:
#                     ArduinoSerial = Serial(arduino_port, 250000, timeout=0.01)
#                     ArduinoSerial.close()
#                     ArduinoSerial.open()
#                 except:
#                     ArduinoSerial = False


# generating main window object
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = PyQt5.QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setWindowIcon(QtGui.QIcon("logo.png"))
widget.setWindowTitle("GRH Home-BCI")
widget.show()

# starting target recording thread
# target_recording_thread = threading.Thread(target=set_target, args=(), daemon=True)
# target_recording_thread.start()

def exit_handler():
    print('shutting down')
    with open("config.json", "r") as config_File:
        config = json.load(config_File)
    blth_name = config['hub_name']
    mac = find_blth_ports(blth_name)
    if mac:
        sck = connect_to_blth(mac)
        send_data(sck, 'R10')
        send_data(sck, 'R20')
        send_data(sck, 'R30')
        send_data(sck, 'R40')
        send_data(sck, 'R50')
try:
    sys.exit(app.exec_())
except:
    atexit.register(exit_handler)


