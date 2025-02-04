import json
from utils import *

'''
    function that handles checking for Emotiv headset connection
'''

def check_headset_connection(user):
    c = Cortex(user, debug_mode=False)
    res = c.query_headset()
    if res:
        return True
    else:
        return False


