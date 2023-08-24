import json
import serial.tools.list_ports


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



