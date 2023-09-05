# Imagination Centre Home-BCI python version 
This Repository contains python source code for building the Home-BCI app. 

## About
Home BCI app allows usage of Emotiv BCI output to emulate key-presses, activate smart-plugs, control a commercial FES device using a third-party hardware (developed locally), and create paintings. 
BCI-Gaiming-Platform and BCI-Paint are two other repositories  that are integrated into this app to allow for paiting and playing games remotely through by using the Emotiv BCI outputs. 

## Getting Started

### Obtain your unique Client ID and Secret 
to use this app, you need to obtain a unique client id and secret from your Emotiv Cortex account. update the user.json file located in the main repository folder with your new client information. 

### Build BCI_Paint and BCI_gaming executables 
in order to open BCI-Paint and BCI_gaming apps through the Home-BCI app, you need to build the executables for each of those app. 
Refer to each repository separately for build instructions. "launch_app.py" is the function that handles opening these two apps externally. 

### Find the arduino COM port and smart-plug's IP Address 
To find the arduino port, after connecting the arduino through usb, either use the arduino IDE or run serial.tools.list_ports.comports() to get a list of connected COM ports. to specify the port you can either adjust the config.json file or change the COM port value in the settings tab of the app and then save settings. 

We've only programmed Kasa smart-plugs into this app for now. to find the IP address for your smart-plug please refer to your router's admin page. 

### running the main app   
