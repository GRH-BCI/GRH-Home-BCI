# Imagination Centre Home-BCI  
This Repository contains Python source code for building the Home-BCI app. 

## About
Home BCI app allows usage of Emotiv BCI output to emulate key presses, activate smart plugs, control a commercial FES device using third-party hardware (developed locally), and create paintings. 
BCI-Gaiming-Platform and BCI-Paint are two other repositories that are integrated into this app to allow for painting and playing games remotely by using the Emotiv BCI outputs. 

## Getting Started

### Obtaining your unique Client ID and Secret 
To use this app, you need to obtain a unique client ID and secret from your Emotiv Cortex account. update the user.json file located in the main repository folder with your new client information. 

### Building BCI_Paint and BCI_gaming executables 
In order to open BCI-Paint and BCI_gaming apps through the Home-BCI app, you need to build the executables for each of that app. 
Refer to each repository separately for build instructions. "launch_app.py" is the function that handles opening these two apps externally. 

### Find the Arduino COM port and smart plug's IP Address 
To find the Arduino port, after connecting the Arduino through USB, either use the Arduino IDE or run serial.tools.list_ports.comports() to get a list of connected COM ports. to specify the port you can either adjust the config.json file or change the COM port value in the settings tab of the app and then save settings. 

We've only programmed Kasa smart plugs into this app for now. To find the IP address for your smart plug please refer to your router's admin page. 

### Building the project 
1. Download the source code
2. Unzip the folder
3. Navigate to the folder in your preferred IDE or in the terminal and run: pyinstaller main.py
4. A 'dist' folder should be created and the executable should be inside the 'main' folder in the 'dist' folder
5. Move or copy the main.exe to the project folder. you need the following files to be in the same path as main.exe: config.json, time_config.json, welcomescreen.ui, user.json, utils folder, assets folder
6. Double-click on main.exe to run the app!
you can alternatively run the source code by running main or opening main.py in your IDE if you have all the dependencies installed: python3 main.py
