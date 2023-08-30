# Imagination Centre Home-BCI python version 
This Repository contains python source code for building the Home-BCI app. 

## About
Home BCI app allows usage of Emotiv BCI output to emulate key-presses, activate smart-plugs, control a commercial FES device using a third-party hardware (developed locally), and create paintings. 
BCI-Gaiming-Platform and BCI-Paint are two other repositories  that are integrated into this app to allow for paiting and playing games remotely through by using the Emotiv BCI outputs. 

## Getting Started

### Obtain your unique Client ID and Secret 
to use this app, you need to obtain a unique client id and secret from your Emotiv Cortex account. update the user.json file located in the main repository folder with your new client information. 
### Build BCI_Paint and BCI_gaming executables 
in order to open BCI-Paint and BCI_gaming apps through the Home-BCI app, you need to build the executables for each of those app. launch_app.py handles  opening external apps. you may need to change the path for opening external executables based on how you build those projects. 
### Find the arduino COM port and smart-plug's IP Address 


    
