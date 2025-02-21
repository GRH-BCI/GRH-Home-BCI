import json
import subprocess
import socket

'''
    check to see if arduino is connected to the specified port. 
'''


def find_blth_ports(AT_name):
    try:
        command = [
            "powershell",
            "-Command",
            "Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq 'OK' } | Format-Table -AutoSize Name,InstanceId"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        devices = result.stdout.strip().split("\n")

        for line in devices[3:]:  # Skip the header lines
            parts = line.split()
            if len(parts) > 1:
                name = " ".join(parts[:-1])
                address = parts[-1]
                if name == AT_name:
                    address = address[-12:]
                    address = ":".join(address[i:i + 2] for i in range(0, len(address), 2))
                    return address
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def connect_to_blth(blth_mac):
    if blth_mac:
        port = 1
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    try:
        # Connect to the device
        sock.connect((blth_mac, port))
        print(f"Connected to {blth_mac} on port {port}")
        return sock
    except Exception as e:
        print(f"Failed to connect to {blth_mac} on port {port}: {e}")
        return None


def send_data(sock, data):
    try:
        if sock:
            sock.send(data.encode('utf-8'))
            print(f"Sent: {data}")
        else:
            print("No valid connection to send data.")
    except Exception as e:
        print(f"Failed to send data: {e}")



def receive_data(sock): # return the data varailbe
    try:
        if sock:
            data = sock.recv(1024).decode('utf-8')
            print(f"Received: {data}")
            return data
        else:
            print("No valid connection to receive data.")
            return None
    except Exception as e:
        print(f"Failed to receive data: {e}")
        return None