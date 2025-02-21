import time
from utils.blth_handler import send_data, connect_to_blth, find_blth_ports
'''
    functions to handle manually switching 
'''

def manual_btn_control(sock, channel):
    if sock:
        if channel == 11:
            send_data(sock,'R11')
        elif channel == 21:
            send_data(sock,'R21')
        elif channel == 31:
            send_data(sock,'R31')
        elif channel == 41:
            send_data(sock,'R41')
        elif channel == 10:
            send_data(sock,'R10')
        elif channel == 20:
            send_data(sock,'R20')
        elif channel == 30:
            send_data(sock,'R30')
        elif channel == 40:
            send_data(sock,'R40')
