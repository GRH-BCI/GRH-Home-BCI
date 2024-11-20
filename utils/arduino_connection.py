import json
import serial.tools.list_ports

'''
    check to see if arduino is connected to the specified port. 
'''
def check_arduino_connection():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    preset_port = config["fes_port"]
    arduino_port = []
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    arduino_port = [port for port in myports if preset_port in port]
    if arduino_port:
        return True
    else:
        return False

def find_arduino_port():
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    myports_desc = [p.description for p in list(serial.tools.list_ports.comports())]
    for port_desc in myports_desc:
        if 'arduino' in (str(port_desc)).lower():
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
            config["fes_port"] = myports[myports_desc.index(port_desc)][0]
            json.dump(config, open("config.json", "w"), indent=4, sort_keys=False)



