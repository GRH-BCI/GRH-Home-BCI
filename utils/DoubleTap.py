import socket
import blth_handler
import threading
import time
import select


address = blth_handler.find_blth_ports("AT-HUB-1")
sock = blth_handler.connect_to_blth(address)

time.sleep(1)
message = ""


# This function will be running in the background until the main program ends
def feedback(sock):
    print("Welcome, Arduino Connected")
    # Run forever
    message = False
    while True:

        ready, _, _ = select.select([sock], [], [], 0.1)  # Timeout of 0.1 seconds
        # Checking if there is data being recieved from the arduino.
        if ready:

            # Read the data and decode it from binary to ascii
            message = blth_handler.receive_data(sock)

            # possible values for message are 
            #'DTB'(and then a number from 1-6), Double Tap Button
            #'TB'(and then a number from 1-6), Tap Button
            #'LGB'(and then a number from 1-6), Let Go Button
            #'HB'(and then a number from 1-6) Hold Button

            # remove the last charecter form message and store it into a variable
        if message:  # Ensure message is not empty
            # print(message)
            button_number = message[-1]
            message = message[:-1]

            if message == 'DTB':
                print(f'Button {button_number} was double tapped')
                # send any signal to the arduino to turn on the relay in here

            elif message == 'TB':
                print(f'Button {button_number} was tapped')
            elif message == 'LGB':
                blth_handler.send_data(sock, '0F')
                print(f'Button {button_number} was let go')
            elif message == 'HB':
                blth_handler.send_data(sock, '0N')
                print(f'Button {button_number} is being held')

daemon_thread = threading.Thread(target=feedback(sock), name="daemon-thread", daemon=True)

daemon_thread.start()