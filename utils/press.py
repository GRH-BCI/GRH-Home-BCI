from pynput.keyboard import Key, Controller

import threading
import time
kb = Controller()

"""
    function for emulating key press and key hold-downs 
"""

def press_n_hold(button, duration):
    kb.press(button)
    curr = time.time()
    while time.time() - curr <= duration:
        pass
    kb.release(button)


def press(button):
    thread = threading.Thread(target=press_n_hold, args=(str(button), 0.1))
    thread.start()