import time
from utils.blth_handler import send_data, connect_to_blth, find_blth_ports
'''
    functions to handle manually switching 
'''

def manual_btn_control(sock, channel):
    if sock:
        if channel == 1:
            send_data(sock,'0N')
        elif channel == 2:
            send_data(sock,'02')
        elif channel == 3:
            send_data(sock,'03')
        elif channel == 4:
            send_data(sock,'04')
        else:
            send_data(sock,'0F')

