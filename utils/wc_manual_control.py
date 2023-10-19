import time

'''
    functions to handle manually switching 
'''

def manual_btn_control(arduinoSerial, channel):
    if arduinoSerial != False:
        if channel == 1:
            arduinoSerial.write(str.encode('0'))
            arduinoSerial.write(str.encode('N'))
        elif channel == 2:
            arduinoSerial.write(str.encode('0'))
            arduinoSerial.write(str.encode('2'))
        elif channel == 3:
            arduinoSerial.write(str.encode('0'))
            arduinoSerial.write(str.encode('3'))
        elif channel == 4:
            arduinoSerial.write(str.encode('0'))
            arduinoSerial.write(str.encode('4'))
        else:
            arduinoSerial.write(str.encode('0'))
            arduinoSerial.write(str.encode('F'))
