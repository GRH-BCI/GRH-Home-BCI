import json
from utils import *

'''
    function that handles checking for Emotiv headset connection
'''

def check_headset_connection():
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

        return True
    except:
        return False