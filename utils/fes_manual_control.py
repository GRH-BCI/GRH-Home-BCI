
import time

'''
    functions to handle manually switching the FES device on/off 
'''

def manual_start(arduinoSerial):
    if arduinoSerial != False:
        arduinoSerial.write(str.encode('0'))
        arduinoSerial.write(str.encode('N'))
        time.sleep(.1)
        arduinoSerial.write(str.encode('0'))
        arduinoSerial.write(str.encode('F'))


def manual_stop(arduinoSerial):
    if arduinoSerial != False:
        arduinoSerial.write(str.encode('0'))
        arduinoSerial.write(str.encode('2'))
        time.sleep(.1)
        arduinoSerial.write(str.encode('0'))
        arduinoSerial.write(str.encode('F'))