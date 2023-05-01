import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter_custom_button import TkinterCustomButton
import train
import threading
import websocket  # 'pip install websocket-client' for install
import json
import ssl
import time
from pydispatch.dispatch import Dispatcher
from pynput.keyboard import Key, Controller
import asyncio
from kasa import Discover
import asyncio
from kasa import SmartPlug

cooper = ('georgia', 20)


class gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "GRH Home-BCI")
        w = 1000
        h = 600
        tk.Tk.geometry(self, '%dx%d+0+0' % (w, h))

        tabControl = ttk.Notebook(self)
        tab_KB = ttk.Frame(tabControl)
        tab_EC = ttk.Frame(tabControl)
        tabControl.add(tab_KB, text='Keyboard')
        tabControl.add(tab_EC, text='Smart Home')
        tabControl.pack(expand=1, fill="both")

        # keyboard tab
        global emotivtext, flag
        flag = tk.StringVar()
        flag.set('go')
        emotivtext = tk.StringVar()
        emotivtext.set("Current Emotiv Command:")
        emotiv_label = tk.Label(tab_KB, textvariable=emotivtext, font=cooper)
        emotiv_label.grid(row=3, column=2, rowspan=2, columnspan=2, padx=10, pady=20)

        pull_key_name = tk.Label(tab_KB, text="Pull Key       ", font=cooper)
        pull_key_name.grid(row=0, column=0, padx=0, pady=10, sticky='E')
        pull_key_var = StringVar(self)
        pull_key_var.set("")

        push_key_name = tk.Label(tab_KB, text="Push Key       ", font=cooper)
        push_key_name.grid(row=0, column=2, padx=0, pady=10, sticky='E')
        push_key_var = StringVar(self)
        push_key_var.set("")

        lift_key_name = tk.Label(tab_KB, text="Lift Key       ", font=cooper)
        lift_key_name.grid(row=1, column=0, padx=0, pady=10, sticky='E')
        lift_key_var = StringVar(self)
        lift_key_var.set("")

        drop_key_name = tk.Label(tab_KB, text="Drop Key       ", font=cooper)
        drop_key_name.grid(row=1, column=2, padx=0, pady=10, sticky='E')
        drop_key_var = StringVar(self)
        drop_key_var.set("")

        left_key_name = tk.Label(tab_KB, text="Left Key       ", font=cooper)
        left_key_name.grid(row=2, column=0, padx=0, pady=10, sticky='E')
        left_key_var = StringVar(self)
        left_key_var.set("")

        right_key_name = tk.Label(tab_KB, text="Right Key     ", font=cooper)
        right_key_name.grid(row=2, column=2, padx=0, pady=10, sticky='E')
        right_key_var = StringVar(self)
        right_key_var.set("")

        pull_key_options = tk.OptionMenu(tab_KB, pull_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                         'left', 'right', '1', '2', '3', '4', '5')
        pull_key_options.config(font=cooper)
        pull_key_options.grid(row=0, column=1, padx=0, pady=10, sticky='W')
        push_key_options = tk.OptionMenu(tab_KB, push_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                         'left', 'right', '1', '2', '3', '4', '5')
        push_key_options.config(font=cooper)
        push_key_options.grid(row=0, column=3, padx=0, pady=10, sticky='W')
        lift_key_options = tk.OptionMenu(tab_KB, lift_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                         'left', 'right', '1', '2', '3', '4', '5')
        lift_key_options.config(font=cooper)
        lift_key_options.grid(row=1, column=1, padx=0, pady=10, sticky='W')
        drop_key_options = tk.OptionMenu(tab_KB, drop_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                         'left', 'right', '1', '2', '3', '4', '5')
        drop_key_options.config(font=cooper)
        drop_key_options.grid(row=1, column=3, padx=0, pady=10, sticky='W')
        left_key_options = tk.OptionMenu(tab_KB, left_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                         'left', 'right', '1', '2', '3', '4', '5')
        left_key_options.config(font=cooper)
        left_key_options.grid(row=2, column=1, padx=0, pady=10, sticky='W')
        right_key_options = tk.OptionMenu(tab_KB, right_key_var, 'w', 'a', 's', 'd', 'g', 'h', 'space', 'up', 'down',
                                          'left', 'right', '1', '2', '3', '4', '5')
        right_key_options.config(font=cooper)
        right_key_options.grid(row=2, column=3, padx=0, pady=10, sticky='W')

        threshold_label = tk.Label(tab_KB, text="Activation threshold: ", font=cooper)
        threshold_label.grid(row=3, column=0, padx=30, pady=10, sticky='W')
        threshold_var = StringVar(self)
        threshold_var.set("50%")
        threshold_options = tk.OptionMenu(tab_KB, threshold_var, '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%',
                                          '90%')
        threshold_options.config(font=cooper)
        threshold_options.grid(row=3, column=1, padx=30, pady=10, sticky='W')
        delay_label = tk.Label(tab_KB, text="Delay time (s):", font=cooper)
        delay_label.grid(row=4, column=0, padx=30, pady=10, sticky='W')
        delay_var = IntVar(self)
        delay_var.set(0)
        delay_options = tk.OptionMenu(tab_KB, delay_var, 0, 1, 2, 3)
        delay_options.config(font=cooper)
        delay_options.grid(row=4, column=1, padx=30, pady=10, sticky='W')

        profile_entry = "GRH-HomeBCI"
        send_button = tk.Button(master=tab_KB, bg='green', text="Send Key", fg="white",
                                          font=cooper, width=8,
                                          command=lambda: start_thread(profile_entry, threshold_var.get(),
                                                                       delay_var.get(),
                                                                       [push_key_var.get(), pull_key_var.get(),
                                                                        lift_key_var.get(), drop_key_var.get(),
                                                                        left_key_var.get(), right_key_var.get()]))
        send_button.grid(row=5, column=0, pady=20, columnspan=4)

        pause_button = tk.Button(master=tab_KB, bg='tomato', text='pause', width=8, fg="white", font = cooper,

                                           command=lambda: stop_thread())
        pause_button.grid(row=5, column=1, pady=30, columnspan=4)

        # smart-home tab
        global dev1_IP_entry_str_1, dev1_IP_entry_str_2, dev1_IP_entry_str_3, dev1_IP_entry_str_4
        global dev2_IP_entry_str_1, dev2_IP_entry_str_2, dev2_IP_entry_str_3, dev2_IP_entry_str_4
        global dev3_IP_entry_str_1, dev3_IP_entry_str_2, dev3_IP_entry_str_3, dev3_IP_entry_str_4
        global dev4_IP_entry_str_1, dev4_IP_entry_str_2, dev4_IP_entry_str_3, dev4_IP_entry_str_4

        # dev 1 to 4 ip address boxes
        dev1_IP_label = tk.Label(master=tab_EC, text="Dev.1 IP Address", font=cooper)
        dev1_IP_label.grid(row=0, column=4, pady=20, sticky='W')
        dev1_IP_entry_str_1 = tk.StringVar()
        dev1_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev1_IP_entry_str_1, font=cooper)
        dev1_IP_entry_str_1.trace("w", lambda *args: character_limit(dev1_IP_entry_str_1))
        dev1_IP_entry.grid(row=0, column=5, padx=2, sticky='W')

        dev1_IP_entry_str_2 = tk.StringVar()
        dev1_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev1_IP_entry_str_2, font=cooper)
        dev1_IP_entry_str_2.trace("w", lambda *args: character_limit(dev1_IP_entry_str_2))
        dev1_IP_entry.grid(row=0, column=6, padx=2, sticky='W')

        dev1_IP_entry_str_3 = tk.StringVar()
        dev1_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev1_IP_entry_str_3, font=cooper)
        dev1_IP_entry_str_3.trace("w", lambda *args: character_limit(dev1_IP_entry_str_3))
        dev1_IP_entry.grid(row=0, column=7, padx=2, sticky='W')

        dev1_IP_entry_str_4 = tk.StringVar()
        dev1_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev1_IP_entry_str_4, font=cooper)
        dev1_IP_entry_str_4.trace("w", lambda *args: character_limit(dev1_IP_entry_str_4))
        dev1_IP_entry.grid(row=0, column=8, padx=2, sticky='W')

        # dev2
        dev2_IP_label = tk.Label(master=tab_EC, text="Dev.2 IP Address", font=cooper)
        dev2_IP_label.grid(row=1, column=4, sticky='W')
        dev2_IP_entry_str_1 = tk.StringVar()
        dev2_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev2_IP_entry_str_1, font=cooper)
        dev2_IP_entry_str_1.trace("w", lambda *args: character_limit(dev2_IP_entry_str_1))
        dev2_IP_entry.grid(row=1, column=5, padx=2, sticky='W')

        dev2_IP_entry_str_2 = tk.StringVar()
        dev2_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev2_IP_entry_str_2, font=cooper)
        dev2_IP_entry_str_2.trace("w", lambda *args: character_limit(dev2_IP_entry_str_2))
        dev2_IP_entry.grid(row=1, column=6, padx=2, sticky='W')

        dev2_IP_entry_str_3 = tk.StringVar()
        dev2_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev2_IP_entry_str_3, font=cooper)
        dev2_IP_entry_str_3.trace("w", lambda *args: character_limit(dev2_IP_entry_str_3))
        dev2_IP_entry.grid(row=1, column=7, padx=2, sticky='W')

        dev2_IP_entry_str_4 = tk.StringVar()
        dev2_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev2_IP_entry_str_4, font=cooper)
        dev2_IP_entry_str_4.trace("w", lambda *args: character_limit(dev2_IP_entry_str_4))
        dev2_IP_entry.grid(row=1, column=8, padx=2, sticky='W')

        # dev3
        dev3_IP_label = tk.Label(master=tab_EC, text="Dev.3 IP Address", font=cooper)
        dev3_IP_label.grid(row=2, column=4, sticky='W')
        dev3_IP_entry_str_1 = tk.StringVar()
        dev3_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev3_IP_entry_str_1, font=cooper)
        dev3_IP_entry_str_1.trace("w", lambda *args: character_limit(dev3_IP_entry_str_1))
        dev3_IP_entry.grid(row=2, column=5, padx=2, sticky='W')

        dev3_IP_entry_str_2 = tk.StringVar()
        dev3_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev3_IP_entry_str_2, font=cooper)
        dev3_IP_entry_str_2.trace("w", lambda *args: character_limit(dev3_IP_entry_str_2))
        dev3_IP_entry.grid(row=2, column=6, padx=2, sticky='W')

        dev3_IP_entry_str_3 = tk.StringVar()
        dev3_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev3_IP_entry_str_3, font=cooper)
        dev3_IP_entry_str_3.trace("w", lambda *args: character_limit(dev3_IP_entry_str_3))
        dev3_IP_entry.grid(row=2, column=7, padx=2, sticky='W')

        dev3_IP_entry_str_4 = tk.StringVar()
        dev3_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev3_IP_entry_str_4, font=cooper)
        dev3_IP_entry_str_4.trace("w", lambda *args: character_limit(dev3_IP_entry_str_4))
        dev3_IP_entry.grid(row=2, column=8, padx=2, sticky='W')

        # dev4
        dev4_IP_label = tk.Label(master=tab_EC, text="Dev.4 IP Address", font=cooper)
        dev4_IP_label.grid(row=3, column=4, sticky='W')
        dev4_IP_entry_str_1 = tk.StringVar()
        dev4_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev4_IP_entry_str_1, font=cooper)
        dev4_IP_entry_str_1.trace("w", lambda *args: character_limit(dev4_IP_entry_str_1))
        dev4_IP_entry.grid(row=3, column=5, padx=2, sticky='W')

        dev4_IP_entry_str_2 = tk.StringVar()
        dev4_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev4_IP_entry_str_2, font=cooper)
        dev4_IP_entry_str_2.trace("w", lambda *args: character_limit(dev4_IP_entry_str_2))
        dev4_IP_entry.grid(row=3, column=6, padx=2, sticky='W')

        dev4_IP_entry_str_3 = tk.StringVar()
        dev4_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev4_IP_entry_str_3, font=cooper)
        dev4_IP_entry_str_3.trace("w", lambda *args: character_limit(dev4_IP_entry_str_3))
        dev4_IP_entry.grid(row=3, column=7, padx=2, sticky='W')

        dev4_IP_entry_str_4 = tk.StringVar()
        dev4_IP_entry = tk.Entry(master=tab_EC, width=3, textvariable=dev4_IP_entry_str_4, font=cooper)
        dev4_IP_entry_str_4.trace("w", lambda *args: character_limit(dev4_IP_entry_str_4))
        dev4_IP_entry.grid(row=3, column=8, padx=2, sticky='W')

        dev_status_label = tk.Label(tab_EC, text="Device Status: ", font=cooper)
        dev_status_label.grid(row=4, column=4, pady=0, columnspan=5, sticky='SW')
        dev_stat_str = tk.StringVar()
        dev_stat_str.set("No device connected!")
        dev_stat = tk.Label(tab_EC, textvariable=dev_stat_str, font=cooper)
        dev_stat.grid(row=5, column=4, padx=0, rowspan=4, columnspan=5, sticky='NW')

        global emotivtext_EC
        emotivtext_EC = tk.StringVar()
        emotivtext_EC.set("Current Emotiv Command:")
        emotiv_label_EC = tk.Label(tab_EC, textvariable=emotivtext_EC, font=cooper)
        emotiv_label_EC.grid(row=6, column=0, rowspan=2, columnspan=4, padx=10, pady=20)

        check_button = TkinterCustomButton(master=tab_EC, bg_color='white', text_color='white',
                                           text="Check for devices", width=200, fg_color="brown",
                                           corner_radius=10, command=lambda: device_check())
        check_button.grid(row=5, column=0, columnspan=4, padx=0, pady=5)

        mode_label = tk.Label(tab_EC, text="Mode ", font=cooper)
        mode_label.grid(row=3, column=0, columnspan=2, padx=0, pady=10, sticky='W')
        global mode_var
        mode_var = StringVar(self)
        mode_var.set("On")
        mode_options = tk.OptionMenu(tab_EC, mode_var, 'On', 'On for 5s', 'On for 30s', 'On for 1m')
        mode_options.config(font=cooper)
        mode_options.grid(row=3, column=1, columnspan=2, padx=0, pady=10, sticky='W')

        pull_dev_name_EC = tk.Label(tab_EC, text="Pull ", font=cooper)
        pull_dev_name_EC.grid(row=0, column=0, padx=0, pady=10, sticky='E')
        pull_dev_var_EC = StringVar(self)
        pull_dev_var_EC.set("")

        push_dev_name_EC = tk.Label(tab_EC, text="Push ", font=cooper)
        push_dev_name_EC.grid(row=0, column=2, padx=0, pady=10, sticky='E')
        push_dev_var_EC = StringVar(self)
        push_dev_var_EC.set("")

        lift_dev_name_EC = tk.Label(tab_EC, text="Lift ", font=cooper)
        lift_dev_name_EC.grid(row=1, column=0, padx=0, pady=10, sticky='E')
        lift_dev_var_EC = StringVar(self)
        lift_dev_var_EC.set("")

        drop_dev_name_EC = tk.Label(tab_EC, text="Drop ", font=cooper)
        drop_dev_name_EC.grid(row=1, column=2, padx=0, pady=10, sticky='E')
        drop_dev_var_EC = StringVar(self)
        drop_dev_var_EC.set("")

        left_dev_name_EC = tk.Label(tab_EC, text="Left ", font=cooper)
        left_dev_name_EC.grid(row=2, column=0, padx=0, pady=10, sticky='E')
        left_dev_var_EC = StringVar(self)
        left_dev_var_EC.set("")

        right_dev_name_EC = tk.Label(tab_EC, text="Right ", font=cooper)
        right_dev_name_EC.grid(row=2, column=2, padx=0, pady=10, sticky='E')
        right_dev_var_EC = StringVar(self)
        right_dev_var_EC.set("")

        pull_dev_options_EC = tk.OptionMenu(tab_EC, pull_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        pull_dev_options_EC.config(font=cooper)
        pull_dev_options_EC.grid(row=0, column=1, padx=0, pady=10, sticky='W')
        push_dev_options_EC = tk.OptionMenu(tab_EC, push_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        push_dev_options_EC.config(font=cooper)
        push_dev_options_EC.grid(row=0, column=3, padx=0, pady=10, sticky='W')
        lift_dev_options_EC = tk.OptionMenu(tab_EC, lift_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        lift_dev_options_EC.config(font=cooper)
        lift_dev_options_EC.grid(row=1, column=1, padx=0, pady=10, sticky='W')
        drop_dev_options_EC = tk.OptionMenu(tab_EC, drop_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        drop_dev_options_EC.config(font=cooper)
        drop_dev_options_EC.grid(row=1, column=3, padx=0, pady=10, sticky='W')
        left_dev_options_EC = tk.OptionMenu(tab_EC, left_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        left_dev_options_EC.config(font=cooper)
        left_dev_options_EC.grid(row=2, column=1, padx=0, pady=10, sticky='W')
        right_dev_options_EC = tk.OptionMenu(tab_EC, right_dev_var_EC, 'Dev.1', 'Dev.2', 'Dev.3', 'Dev.4')
        right_dev_options_EC.config(font=cooper)
        right_dev_options_EC.grid(row=2, column=3, padx=0, pady=10, sticky='W')

        threshold_dev_label_EC = tk.Label(tab_EC, text="Activation threshold: ", font=cooper)
        threshold_dev_label_EC.grid(row=4, column=0, columnspan=3, padx=0, pady=10, sticky='W')
        threshold_dev_var_EC = StringVar(self)
        threshold_dev_var_EC.set("50%")
        threshold_dev_options_EC = tk.OptionMenu(tab_EC, threshold_dev_var_EC, '10%', '20%', '30%', '40%', '50%', '60%',
                                                 '70%', '80%',
                                                 '90%')
        threshold_dev_options_EC.config(font=cooper)
        threshold_dev_options_EC.grid(row=4, column=3, padx=(0, 30), pady=10, sticky='W')

        strt_button_EC = TkinterCustomButton(master=tab_EC, bg_color='white', text="Start", width=200, fg_color="green",
                                             corner_radius=10,
                                             command=lambda: start_thread_EC(profile_entry, threshold_dev_var_EC.get(),
                                                                             delay_var.get(),
                                                                             [push_dev_var_EC.get(),
                                                                              pull_dev_var_EC.get(),
                                                                              lift_dev_var_EC.get(),
                                                                              drop_dev_var_EC.get(),
                                                                              left_dev_var_EC.get(),
                                                                              right_dev_var_EC.get()]))
        strt_button_EC.grid(row=9, column=0, columnspan=5, padx=20, pady=20)

        # handling resize
        tab_KB.grid_columnconfigure(0, weight=1)
        tab_KB.grid_columnconfigure(1, weight=1)
        tab_KB.grid_columnconfigure(2, weight=1)
        tab_KB.grid_columnconfigure(3, weight=1)
        tab_KB.grid_columnconfigure(4, weight=1)
        tab_KB.grid_columnconfigure(5, weight=1)
        tab_KB.grid_columnconfigure(6, weight=1)
        tab_KB.grid_columnconfigure(7, weight=1)
        tab_KB.grid_rowconfigure(0, weight=1)
        tab_KB.grid_rowconfigure(1, weight=1)
        tab_KB.grid_rowconfigure(2, weight=1)
        tab_KB.grid_rowconfigure(3, weight=1)
        tab_KB.grid_rowconfigure(4, weight=1)
        tab_KB.grid_rowconfigure(5, weight=1)
        tab_KB.grid_rowconfigure(6, weight=1)
        tab_KB.grid_rowconfigure(7, weight=1)
        tab_KB.grid_rowconfigure(8, weight=1)
        tab_KB.grid_rowconfigure(9, weight=1)

        tab_EC.grid_columnconfigure(0, weight=1)
        tab_EC.grid_columnconfigure(1, weight=1)
        tab_EC.grid_columnconfigure(2, weight=1)
        tab_EC.grid_columnconfigure(3, weight=1)
        tab_EC.grid_columnconfigure(4, weight=1)
        tab_EC.grid_columnconfigure(5, weight=1)
        tab_EC.grid_columnconfigure(6, weight=1)
        tab_EC.grid_columnconfigure(7, weight=1)
        tab_EC.grid_rowconfigure(0, weight=1)
        tab_EC.grid_rowconfigure(1, weight=1)
        tab_EC.grid_rowconfigure(2, weight=1)
        tab_EC.grid_rowconfigure(3, weight=1)
        tab_EC.grid_rowconfigure(4, weight=1)
        tab_EC.grid_rowconfigure(5, weight=1)
        tab_EC.grid_rowconfigure(6, weight=1)
        tab_EC.grid_rowconfigure(7, weight=1)
        tab_EC.grid_rowconfigure(8, weight=1)
        tab_EC.grid_rowconfigure(9, weight=1)

        # user info
        # GRHbci
        # user = {
        #     "license": "",
        #     "client_id": "xAciQLFGunJqagvVY0rrbHHaNyWj28x0IRbZYNit",
        #     "client_secret": "GRNKsYVsb2qgcBZtsO2JTVV1NeuzNhPyZJWmw3KsecbLiVwK2ffyphzr9mUTL65WcMLzqdy5KBGiFekybb26Qx3OPm9U2o13K2lTSI49feO6H24IwDifkGDS2iHRqujC",
        #     "debit": 100
        # }
        user = {
            "license": "",
            "client_id": "zIAnMwcxpC8A47PdjTzOPKY4MyIkWwEiBrtInXvT",
            "client_secret": "69BMfbZtH9A7Mw0IV87p9yhXmJsNGF2XWatnUWwftecnws4hxJ9e3X6sN7i3qanwZyfngPm2sCQMreaSEAVXwHbOmx1gTgbfkxKcStfBtUZnal7FqeXoUF2FXf9bQLpo",
            "debit": 100
        }

        user2 = {
            "license": "",
            "client_id": "JLuMZwsnMkvrEo5eGR7wwazyXRfjdBBg1KnGC5id",
            "client_secret": "f2tHNJAVA5O2eza6GkPX5DeZni8J7TW2tI3IuO6YFISdxGmGBtLLm2SvpMTz53TGLvPiZJMw45Mnljnjt1UCSc7r7FXvjcsUOGOB6DHJbg6GU06NtbLCqRiRIDQiDyFz",
            "debit": 100
        }

        user3 = {
            "license": "",
            "client_id": "UDF74j9A3YE8sp13A3BPb9SuPH8uBo5kOX9rKlcZ",
            "client_secret": "bjqJC9mGc1JLSkIdfBoVtySzo007b7B7gi4xwG8B4Q71oMSdM1dYgHuvwcemWs6y5rHuZCLVjjhkxTdRl2Am368R63VaYJKpcgOHbSrVT9vQyYESkux4a5qeCvIMOWWN",
            "debit": 100
        }

        user4 = {
            "license": "",
            "client_id": "PFD8kGY0xgFFXgnH1Yg7Dm77OqueRP39apsU0RDR",
            "client_secret": "grSnDWYe18x3deJ7yntynqGnc1rvJbELd23L06g8XzEQpJ8tt2SnIvWsSRhMAO6boEC1phdK4SaVvF2Y49cjYHbOax5QlC9S1qZLf1RACs6tLQNTURNDt1laQtn1rxNe",
            "debit": 100
        }

        user5 = {
            "license": "",
            "client_id": "cNHWGqSgGL8XkwADIOSMOcYLiAJnN0yglA1ABPyP",
            "client_secret": "f18GFszI2pV5DZb1v2SPadul9pB2k8K7hz03zz4mJoyea2oqT6ej0SQWKPS95fkAAIM8B03A4ppZAK9j2dPIeDnyLteUpn2C1ZfiNWvGfFPpFj9DQ34FcXicIeLXXqYJ",
            "debit": 100
        }

        user6 = {
            "license": "",
            "client_id": "Rv2DOlaqT0vNmAEvT1Ht0GyTofMmHj2ojMtuH0i0",
            "client_secret": "hO2GKGh7gVufqKcDeShLZSUbQ7eR2hqVOyt2YtUg88SQc5Rb9yQYdoeU5LjkhekI8ga7Jd7rBCpjB48zfievQlbpti72C3G046HUcnHQQLPyRddlWrGuDdvbf3FfYDgF",
            "debit": 100
        }

        user7 = {
            "license": "",
            "client_id": "E41W7lO3847qB7qFN6t5Ygec21b2uU7wQTG8laTD",
            "client_secret": "tXyJqAxWzshYwOVhUyTOnpfyS9O4ULvzoN8cmYOwU8mBlQ6Wbz8eiE0DksVBaJAhOEMwSPrE4p0b3K25HoD4680HJIRNWBAnuvdFyP8TrfRwGOXJgxhlwvg3ZGdWr6Ic",
            "debit": 100
        }

        def character_limit(entry_text):
            if len(entry_text.get()) > 3:
                entry_text.set(entry_text.get()[-3:])

        def get_IP(ip1, ip2, ip3, ip4):
            res = ""
            res = str(ip1.get()) + '.' + str(ip2.get()) + '.' + str(ip3.get()) + '.' + str(ip4.get())

            return res

        # # KAdams
        # user = {
        #     "license": "",
        #     "client_id": "dHuZLhxmpDnzKeB1ISs8MMxlZeBqnAsxU8g3juuV	",
        #     "client_secret": "secret: e4ix6KF73LOkEnogA5Fm3fpA8rVRPHlhvauvHGVfVQVIcgEhKjaAYsTVvBFwEQrMIRZZhDvEpRi4Z8P7y2CSroCwqW9yih3YhzvWVcy2HOwUQhRZuq8zsRyXp7F4rXQm",
        #     "debit": 100
        # }

        def temp_thread(profile, threshold, dly, key):
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
                while True:
                    c.sub_request_GRH(stream, threshold, dly, key)

            except:
                global emotivtext
                emotivtext.set("No headset connected!")

        def temp_thread_EC(profile, threshold, dly, dev):

            # try:
            global plug_prev_state

            plug_prev_state = tk.StringVar()
            plug_prev_state.set('off')
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

                while True:
                    c.sub_request_GRH_EC(stream, threshold, dly, dev)

            except:
                global emotivtext_EC
                emotivtext_EC.set("No headset connected!")

        def start_thread(profile, threshold, dly, key):
            global flag
            flag.set('go')
            send_thread = threading.Thread(target=temp_thread, args=[profile, threshold, dly, key], daemon=True)
            send_thread.start()

        def start_thread_EC(profile, threshold, dly, dev):
            send_thread = threading.Thread(target=temp_thread_EC, args=[profile, threshold, dly, dev], daemon=True)
            send_thread.start()

        def stop_thread():
            global flag
            identifier = flag.get()
            print(identifier)
            if identifier == 'stop':
                flag.set('go')
                pause_button.config(text="pause")
                pause_button.config(bg='tomato')


            elif identifier == 'go':
                flag.set('stop')
                pause_button.config(text="resume")
                pause_button.config(bg='LimeGreen')

        def device_check():
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            ip_1 = get_IP(dev1_IP_entry_str_1, dev1_IP_entry_str_2, dev1_IP_entry_str_3, dev1_IP_entry_str_4)
            ip_2 = get_IP(dev2_IP_entry_str_1, dev2_IP_entry_str_2, dev2_IP_entry_str_3, dev2_IP_entry_str_4)
            ip_3 = get_IP(dev3_IP_entry_str_1, dev3_IP_entry_str_2, dev3_IP_entry_str_3, dev3_IP_entry_str_4)
            ip_4 = get_IP(dev4_IP_entry_str_1, dev4_IP_entry_str_2, dev4_IP_entry_str_3, dev4_IP_entry_str_4)
            dev_1 = SmartPlug(str(ip_1))
            dev_2 = SmartPlug(str(ip_2))
            dev_3 = SmartPlug(str(ip_3))
            dev_4 = SmartPlug(str(ip_4))
            dev_stat_str_temp = tk.StringVar()
            dev_stat_str_temp.set("")
            if len(ip_1) > 5:
                print(ip_1)
                try:
                    asyncio.run(dev_1.update())
                    dev_stat_str.set(dev_stat_str_temp.get() + "\n" + str(dev_1.model + "  is connected!"))
                    dev_stat_str_temp.set(dev_stat_str.get())
                except:
                    dev_stat_str.set(dev_stat_str.get() + "\n" + "device_1 not connected!")
                    dev_stat_str_temp.set(dev_stat_str.get())

            if len(ip_2) > 5:
                print(ip_2)
                try:
                    asyncio.run(dev_2.update())
                    dev_stat_str.set(dev_stat_str_temp.get() + "\n" + str(dev_2.model + "  is connected!"))
                    dev_stat_str_temp.set(dev_stat_str.get())
                except:
                    dev_stat_str.set(dev_stat_str.get() + "\n" + "device_2 not connected!")
                    dev_stat_str_temp.set(dev_stat_str.get())

            if len(ip_3) > 5:
                try:
                    asyncio.run(dev_3.update())
                    dev_stat_str.set(dev_stat_str_temp.get() + "\n" + str(dev_3.model + "  is connected!"))
                    dev_stat_str_temp.set(dev_stat_str.get())
                except:
                    dev_stat_str.set(dev_stat_str.get() + "\n" + "device_3 not connected!")
                    dev_stat_str_temp.set(dev_stat_str.get())

            if len(ip_4) > 5:
                try:
                    asyncio.run(dev_4.update())
                    dev_stat_str.set(dev_stat_str_temp.get() + "\n" + str(dev_4.model + "  is connected!"))
                    dev_stat_str_temp.set(dev_stat_str.get())

                except:
                    dev_stat_str.set(dev_stat_str.get() + "\n" + "device_4 not connected!")
                    dev_stat_str_temp.set(dev_stat_str.get())


kb = Controller()

def press_n_hold(button,duration):
    kb.press(button)
    curr = time.time()
    while time.time() - curr <= duration:
        pass
    kb.release(button)

def press(button):
    thread = threading.Thread(target=press_n_hold, args=(str(button), 0.1))
    thread.start()


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

    def sub_request_GRH(self, stream, threshold, delay, key):
        global emotivtext, flag

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
        with open("time_config.json", "r") as config_file:
            config = json.load(config_file)
        temp_time = config["time"]

        # while True:
        new_data = self.ws.recv()
        # Then emit the change with optional positional and keyword arguments
        result_dic = json.loads(new_data)

        if result_dic.get('com') != None:
            com_data = {}
            com_data['action'] = result_dic['com'][0]
            com_data['power'] = result_dic['com'][1]
            com_data['time'] = result_dic['time']
            threshold = threshold[0:2]
            self.emit('new_com_data', data=com_data)
            emotivtext.set(f"current Emotiv Command:\n {com_data['action']}, {com_data['power']}")
            if com_data['action'] == 'push' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[0] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[0] == 'space':
                    press(Key.space)
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
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)

            elif com_data['action'] == 'pull' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[1] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[1] == 'space':
                    press(Key.space)
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
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)


            elif com_data['action'] == 'lift' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[2] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[2] == 'space':
                    press(Key.space)
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
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)
            elif com_data['action'] == 'drop' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[3] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[3] == 'space':
                    press(Key.space)
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
            elif com_data['action'] == 'left' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[4] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[4] == 'space':
                    press(Key.space)
                elif key[4] == 'up':
                    press(Key.up)
                elif key[4] == 'down':
                    press(Key.down)
                elif key[4] == 'right':
                    press(Key.right)
                elif key[4] == 'left':
                    press(Key.left)
                else:
                    press((key[4]))

            elif com_data['action'] == 'right' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if key[5] == '':
                    print("please assign a corresponding keyboard key to this command")
                elif key[5] == 'space':
                    press(Key.space)
                elif key[5] == 'up':
                    press(Key.up)
                elif key[5] == 'down':
                    press(Key.down)
                elif key[5] == 'right':
                    press(Key.right)
                elif key[5] == 'left':
                    press(Key.left)
                else:
                    press((key[5]))

                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)

            elif com_data['action'] == 'neurtal':
                print('neutral')
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

    def sub_request_GRH_EC(self, stream, threshold, delay, dev):
        global emotivtext_EC, flag, mode_var

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

        # if result_dic.get('error') != None:
        #     print("subscribe get error: " + result_dic['error']['message'])
        #
        #     return
        # else:
        #
        #     # handle data lable
        #     for stream in result_dic['result']['success']:
        #         stream_name = stream['streamName']
        #         stream_labels = stream['cols']
        #         # ignore com and fac data label because they are handled in on_new_data
        #         if stream_name != 'com' and stream_name != 'fac':
        #             self.extract_data_labels(stream_name, stream_labels)

        # Handle data event
        with open("time_config.json", "r") as config_file:
            config = json.load(config_file)
        temp_time = config["time"]

        # while True:
        new_data = self.ws.recv()
        # Then emit the change with optional positional and keyword arguments
        result_dic = json.loads(new_data)

        def get_IP(ip1, ip2, ip3, ip4):
            res = ""
            res = str(ip1.get()) + '.' + str(ip2.get()) + '.' + str(ip3.get()) + '.' + str(ip4.get())

            return res

        global dev1_IP_entry_str_1, dev1_IP_entry_str_2, dev1_IP_entry_str_3, dev1_IP_entry_str_4
        global dev2_IP_entry_str_1, dev2_IP_entry_str_2, dev2_IP_entry_str_3, dev2_IP_entry_str_4
        global dev3_IP_entry_str_1, dev3_IP_entry_str_2, dev3_IP_entry_str_3, dev3_IP_entry_str_4
        global dev4_IP_entry_str_1, dev4_IP_entry_str_2, dev4_IP_entry_str_3, dev4_IP_entry_str_4
        ip_1 = get_IP(dev1_IP_entry_str_1, dev1_IP_entry_str_2, dev1_IP_entry_str_3, dev1_IP_entry_str_4)
        ip_2 = get_IP(dev2_IP_entry_str_1, dev2_IP_entry_str_2, dev2_IP_entry_str_3, dev2_IP_entry_str_4)
        ip_3 = get_IP(dev3_IP_entry_str_1, dev3_IP_entry_str_2, dev3_IP_entry_str_3, dev3_IP_entry_str_4)
        ip_4 = get_IP(dev4_IP_entry_str_1, dev4_IP_entry_str_2, dev4_IP_entry_str_3, dev4_IP_entry_str_4)
        dev_stat_str_temp = tk.StringVar()
        dev_stat_str_temp.set("")

        async def handle_device(ip):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            global plug_prev_state, mode_var
            plug_state = plug_prev_state.get()

            mode = mode_var.get()
            print(mode)
            p = SmartPlug(ip)
            await p.update()  # Request the update
            print(p.is_on)
            if mode == 'On':
                await p.turn_on()
                plug_prev_state.set('on')
            elif mode == "On for 5s":
                await p.update()  # Request the update
                await p.turn_on()
                await asyncio.sleep(5)
                await p.update()
                await p.turn_off()
                plug_prev_state.set('off')


            elif mode == "On for 30s":
                await p.update()  # Request the update
                await p.turn_on()
                await asyncio.sleep(30)
                await p.update()
                await p.turn_off()
                plug_prev_state.set('off')

            elif mode == "On for 1m":
                await p.update()  # Request the update
                await p.turn_on()
                await asyncio.sleep(60)
                await p.update()
                await p.turn_off()
                plug_prev_state.set('off')




        if result_dic.get('com') != None:
            com_data = {}
            com_data['action'] = result_dic['com'][0]
            com_data['power'] = result_dic['com'][1]
            com_data['time'] = result_dic['time']
            threshold = threshold[0:2]
            self.emit('new_com_data', data=com_data)
            emotivtext_EC.set(f"current Emotiv Command:\n {com_data['action']}, {com_data['power']}")

            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            if com_data['action'] == 'push' and 100 * float(com_data['power']) >= int(
                    threshold) and flag.get() != 'stop':
                if dev[0] == '':
                    print("please assign a corresponding device key to this command")
                elif dev[0] == 'Dev.1':
                    if len(ip_1) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_1)))
                        except:
                            print("dev.1 not responding")
                elif dev[0] == 'Dev.2':
                    if len(ip_2) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_2)))
                        except:
                            print("dev.2 not responding")
                elif dev[0] == 'Dev.3':
                    if len(ip_3) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_3)))
                        except:
                            print("dev.3 not responding")
                elif dev[0] == 'Dev.4':
                    if len(ip_4) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_4)))
                        except:
                            print("dev.4 not responding")
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)
            elif com_data['action'] == 'pull' and 100 * float(com_data['power']) >= int(
                    threshold) and flag.get() != 'stop':
                if dev[1] == '':
                    print("please assign a corresponding device key to this command")
                elif dev[1] == 'Dev.1':
                    if len(ip_1) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_1)))
                        except:
                            print("dev.1 not responding")
                elif dev[1] == 'Dev.2':
                    if len(ip_2) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_2)))
                        except:
                            print("dev.2 not responding")
                elif dev[1] == 'Dev.3':
                    if len(ip_3) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_3)))
                        except:
                            print("dev.3 not responding")
                elif dev[1] == 'Dev.4':
                    if len(ip_4) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_4)))
                        except:
                            print("dev.4 not responding")
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)
            elif com_data['action'] == 'lift' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if dev[2] == '':
                    print("please assign a corresponding device key to this command")
                elif dev[2] == 'Dev.1':
                    if len(ip_1) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_1)))
                        except:
                            print("dev.1 not responding")
                elif dev[2] == 'Dev.2':
                    if len(ip_2) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_2)))
                        except:
                            print("dev.2 not responding")
                elif dev[2] == 'Dev.3':
                    if len(ip_3) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_3)))
                        except:
                            print("dev.3 not responding")
                elif dev[2] == 'Dev.4':
                    if len(ip_4) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_4)))
                        except:
                            print("dev.4 not responding")
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)
            elif com_data['action'] == 'drop' and 100 * float(com_data['power']) >= int(threshold) and (
                    float(com_data['time']) - temp_time) >= delay and flag.get() != 'stop':
                if dev[3] == '':
                    print("please assign a corresponding device key to this command")
                elif dev[3] == 'Dev.1':
                    if len(ip_1) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_1)))
                        except:
                            print("dev.1 not responding")
                elif dev[3] == 'Dev.2':
                    if len(ip_2) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_2)))
                        except:
                            print("dev.2 not responding")
                elif dev[3] == 'Dev.3':
                    if len(ip_3) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_3)))
                        except:
                            print("dev.3 not responding")
                elif dev[3] == 'Dev.4':
                    if len(ip_4) > 5:
                        try:
                            asyncio.run(handle_device(str(ip_4)))
                        except:
                            print("dev.4 not responding")
                config["time"] = float(com_data['time'])
                json.dump(config, open("time_config.json", "w"), indent=4, sort_keys=True)

            elif com_data['action'] == 'neurtal':
                print('neutral')
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

    def train_request(self, detection, action, status):
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

        if detection == 'facialExpression':
            start_wanted_result = 'FE_Succeeded'
            accept_wanted_result = 'FE_Completed'

        if status == 'start':
            wanted_result = start_wanted_result
            print('\n YOU HAVE 8 SECONDS FOR TRAIN ACTION {} \n'.format(action.upper()))

        if status == 'accept':
            wanted_result = accept_wanted_result

        # wait until success
        while True:
            result = self.ws.recv()
            result_dic = json.loads(result)

            print(json.dumps(result_dic, indent=4))

            if 'sys' in result_dic:
                # success or complete, break the wait
                if result_dic['sys'][1] == wanted_result:
                    break

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

    def get_mental_command_action_sensitivity(self, profile_name):
        print('get mental command sensitivity ------------------')
        sensitivity_request = {
            "id": SENSITIVITY_REQUEST_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActionSensitivity",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "status": "get"
            }
        }
        if self.debug:
            print('get mental command sensitivity \n', json.dumps(sensitivity_request, indent=4))

        self.ws.send(json.dumps(sensitivity_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        print(json.dumps(result_dic, indent=4))
        return result_dic

    def set_mental_command_action_sensitivity(self,
                                              profile_name,
                                              values):
        print('set mental command sensitivity ------------------')
        sensitivity_request = {
            "id": SENSITIVITY_REQUEST_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActionSensitivity",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "session": self.session_id,
                "status": "set",
                "values": values
            }
        }
        if self.debug:
            print('set mental command sensitivity \n', json.dumps(sensitivity_request, indent=4))

        self.ws.send(json.dumps(sensitivity_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_active_action(self, profile_name):
        print('get mental command active action ------------------')
        command_active_request = {
            "id": MENTAL_COMMAND_ACTIVE_ACTION_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActiveAction",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "status": "get"
            }
        }

        self.ws.send(json.dumps(command_active_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        print(json.dumps(result_dic, indent=4))

    def set_mental_command_active_action(self, actions):
        print('set mental command active action ------------------')
        command_active_request = {
            "id": SET_MENTAL_COMMAND_ACTIVE_ACTION_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActiveAction",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "status": "set",
                "actions": actions
            }
        }

        if self.debug:
            print('set mental command active action \n', json.dumps(command_active_request, indent=4))

        self.ws.send(json.dumps(command_active_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_brain_map(self, profile_name):
        print('get mental command brain map ------------------')
        brain_map_request = {
            "id": MENTAL_COMMAND_BRAIN_MAP_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandBrainMap",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "session": self.session_id
            }
        }

        self.ws.send(json.dumps(brain_map_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_training_threshold(self, profile_name):
        print('get mental command training threshold -------------')
        training_threshold_request = {
            "id": MENTAL_COMMAND_TRAINING_THRESHOLD,
            "jsonrpc": "2.0",
            "method": "mentalCommandTrainingThreshold",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id
            }
        }

        self.ws.send(json.dumps(training_threshold_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------


app = gui()
app.mainloop()
