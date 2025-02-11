import time
from utils.blth_handler import send_data
'''
    functions to handle manually switching the FES device on/off 
'''

def manual_start(AT_sock):
    send_data(AT_sock, "0N")
    time.sleep(.1)
    send_data(AT_sock, "0F")


def manual_stop(AT_sock):
    send_data(AT_sock, "02")
    time.sleep(.1)
    send_data(AT_sock, "0F")