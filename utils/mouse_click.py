
from pynput.mouse import Controller as mouse_controller
from pynput.mouse import Button as mouse_Button
import threading
import time


kb = mouse_controller()

"""
    function for emulating key press and key hold-downs 
"""

def mouse_press_n_hold(button, duration):
    kb.press(button)
    curr = time.time()
    while time.time() - curr <= duration:
        pass
    kb.release(button)


def mouse_click(button):
    thread = threading.Thread(target=mouse_press_n_hold, args=(button, 0.1))
    thread.start()

