# Docs

## Navigating the Repository

The repository contains a folder for each sub-system named appropriately. In these folders you will find scripts relevant to the sub-system.

Please find a list of all the files in the repository and their purposes below:

| file | purpose |
| --- | --- |
| `haptic_input/arduinoRecordAndPlaySequence` | [NOT USED] A script where the user can record a sequence of button presses, which is then played back using corresponding LEDs on an Arduino. |
| `haptic_input/haptic_input_test_script` | Script to test all the haptic signals played by the remote. Refer to Kaif Kutchwala’s Individual Report for more details. |
| `haptic_input/haptic_input_v1.py` | [NOT USED] Haptic Input script for iteration 1 of haptic input |
| `haptic_input/haptic_input_v2.py` | Script for haptic remote ran on the pico W. |
| `haptic_output/haptic_output_pico.py` | Script for haptic belt ran on the pico W. |
| `haptic_output/haptic_output_v2.py` | Haptic Output Class implementation for V2. |
| `haptic_output/haptic_output.py` | Haptic Output Class implementation for V1. |
| `haptic_output/single_motor_test.py` | Script to test each motor on the haptic belt for V1. |
| `haptic_output/testScript.py` | Script to test accuracy in interpreting directions between position of motors and intensity of vibration. |
| `localisation/localisation.py` | Localisation Class implementation for V1 |
| `localisation/localisationv2.py` | Localisation Class implementation for V2 |
| `localisation/test_bno055.py` | Script to test bno055 sensor with Raspberry Pi 4 |
| `localisation/dwmo1001_*.py` | Library files for interfacing with DWM1001 devices (UWB anchors/tags/listeners) |
| `path_planning/map.py` | Contains binary maps for different areas including the AEL lab and the Mech Eng Foyer |
| `path_planning/path_planning.py` | Path Planner Class Implementation with methods for calculating next direction and more. |
| `.gitignore` | Lists files to not upload to git |
| `apiv1.py` | API script for V1 |
| `apiv2.py` | API script for V2 |
| `control_script.py` | Simple script that sends requests to /update endpoint of api. |
| `dwmo1001_*.py` | Library files for interfacing with DWM1001 devices (UWB anchors/tags/listeners) |
| `README.md` | Readme File |
| `run.sh` | Bash script to start api server |
| `store.json` | JSON store for sequence-location mappings and destination. |
| `testapi.py` | API script for testing efficiency. |

## Setting Up Your Development Environment

### Cloning the GitHub Repository

In order to access all the code and files you need to first clone the GitHub repository. To do this ensure you have `git` installed. Then open a terminal and navigate to the folder you want the repository to be cloned and execute the command: 

`git clone https://github.com/uol-eps-mech/haptic-navigation-aid.git`

### Install Thonny

Thonny is the IDE you will be using to run/debug code on the Pico Ws. 

It can be downloaded from: https://thonny.org/

For instructions on how to use Thonny or setup a new Pico W using Thonny refer to:

```
https://projects.raspberrypi.org/en/projects/get-started-pico-w
```

### Install all dependencies

**API**

- To be able to start up the **API** you need to have `fastapi` installed (`uvicorn` is installed with fastapi).
    - This can be done by executing `pip install fastpi`
- For the localisation module to work you need:
    - pyserial to be installed: `pip install pyserial`
    - You also need to connect the UWB listener to the laptop/device on which the server/api is running. For a windows PC to recognise the DWM1001 tag (UWB listener) you need J-Link drivers to be installed this can be done via this url:
        - https://www.segger.com/downloads/jlink/JLink_Windows_V788j_x86_64.exe
        - Ensure that once the drivers are installed and the listener is plugged in you can see a J-Link device connected under `Devices and Printers` in the control panel.

**Belt**

The Pico W on the belt requires the `picozero` package to be installed. This can be done via Thonny through the `manage packages` option under the `Tools` menu. 

![Thonny1](https://i.imgur.com/7QX4hZn.png)

Make sure to have the Pico W selected in the bottom right corner:

![Thonny2](https://i.imgur.com/JyvxoTP.png)

**Remote**

The Pico W on the remote also requires the `picozero` package to be installed. This can be done as shown above.


## Architecture

### V1

V1 features 2 components, a haptic belt and a haptic remote. The Belt consists of 4 erm motors placed around the waist, a raspberry pi, a power source, a UWB listener, a custom pcb, a bno055 sensor and a i2c multiplexer. To read more about how V1 works refer to Kaif Kutchwala’s report and the group report.

### V2

The purpose for V2 is to further modularise the system and make it more compact. In doing so, we make the system much more user-friendly and robust. 

Instead of only 2 components V2 separates the haptic belt from the web api/server eliminating the need for a raspberry pi and improving the responsiveness and reliability of the web connections. 

The haptic belt now employs a rapsberry pi pico W which hosts its own web api/server that listens for various requests. These requests can be to control the motors or get heading from the onboard bno055 absolute orientation sensor. The belt also requires a power bank as the power source and hosts a uwb sensor that functions as a tag required to get the location of the user.

The Web API now can be hosted on any device including a raspberry pi. The benefit of this is that a much more powerful device (relative to the pi) can be used for much faster processing/computation times and a reliable wireless connection between all 3 components.

The haptic remote functions as in V1.

Each module can be replaced as long as functionality is maintained for different/better/cheaper hardware or improved software without affecting the other modules. For example if a the haptic remote is not convenient and the user prefers a mobile app, the remote can be easily swapper for a mobile app.

![Architecture V1](https://i.imgur.com/8gcZnpv.png)

## Testing individual components:

Each subsystem folder in the repository contains scripts to test the subsystem.

### Haptic Output

The haptic output folder contains a `single_motor_test.py` which allows testing each individual motor by simply calling `python single_motor_test.py <motor_id_here>`` in the terminal.

### Localisation

The localisation scripts contain functions to test both the bno055 sensor and the UWB system to get heading and positional data printed to the terminal. Simply add code to call those functions in the script and run the appropriate python file in the terminal.

## Starting up the Device:

In order to turn the device on there are four main steps:

### Localisation - Set up the UWB anchors

The localisation system relies on Qorvo UWB sensors. These should be placed around the mapped area and their x,y and z coordinates must be noted. 

Each sensor must be configured within the DRTLS  app (not available on Apple) examples are shown in the images below.

The Qorvo sensors can be be configured as 

1. **Tags -** moving objects we want to track)
2. **Anchors -** static sensors placed around the environment to track Tags 
3. **Listeners -** (aka passive anchors in the DRTLS app) that must be connected to the laptop/raspberry pi in order to access a network of anchors and tags and get location data

One of the sensors should be set up as a ‘Listener’ and one should be set up as a ‘Tag’, the rest are ‘Standard’ anchors. You can confirm the anchors are setup properly by looking at the Grid View.

**Note that one anchor must be set as the _initiator_ for the system to work.**

It is possible that the anchors will automatically assign themselves to an existing network, you may need to go into that existing network and change the Tag’s network in the Tag’s settings. It is also advised that you name the anchors for easy debugging. Once the network is set up, the ‘Tag’ should be visible on the grid as shown in the Grid View example image.

![Examples](https://i.imgur.com/mySJhec.png)

### Haptic Belt

1. Ensure that you are facing towards the right as per the map stored in `map.py`
2. Connect the Pico W to the power supply. 
3. Once the Pico W has connected to the WiFi network the belt will vibrate twice and the LED on board the Pico W will turn on.
4. If something has gone wrong on startup the belt will vibrate three times. At this point, connect the Pico W to your laptop/PC and debug/run the code on Thonny to debug.
    1. If this issue is that it isn’t connecting to the WiFi network, try disconnecting the power supply and reconnecting it to the Pico W.  

The belt is now active.

### Web API V1

In V1 the api runs on the raspberry pi and therefore there are 2 ways to host it. 

**Through Raspberry Pi UI**

1. Connect the Raspberry Pi to a monitor.
2. Login and open a terminal
3. Navigate to the repository
4. execute the command `sh run.sh`

**SSH into the Raspberry Pi**

1. SSH into the raspberry pi (refer to this url for help: https://www.makeuseof.com/how-to-ssh-into-raspberry-pi-remote/) 
    
    `ssh <username_here>@<rpi_ip_address_here>`
    
2. Login and navigate to the repository
3. execute the command `sh run.sh`

### Web API V2

1. Open `apiv2.py`
2. To start up the web API simply open a terminal, navigate to the folder `haptic-navigation-aid` or the root folder if it is called something else.
3. Execute the command `uvicorn apiv2:app --host 0.0.0.0 --reload` or `sh [run.sh](http://run.sh)` the second command will run a script that will execute the necessary commands to host the api.
4. Enter the COM port the listener is connected to

Let’s understand this command better. `uvicorn` is what we use to start up the server/api. It needs to know which file the api sits in and what the name of the FastAPI object variable is. Hence why we specify `apiv2` which is the name of the file `[apiv2.py](http://apiv2.py)` followed by a `:` and then the name of the FastAPI object variable `app` as seen in the code:

![fastapi](https://i.imgur.com/N2WZomn.png)

Following this we specify a few requirements. Firstly, we set the `--host` flag to `0.0.0.0` which tell uvicorn to host the API on `[localhost](http://localhost)`. Secondly, we set the `--reload` flag, this should be used during debugging only as it reloads the API every time a change to any dependency is made i.e. any file used by the API. This makes the development process much quicker but should be turned off during demos/trials.

### Haptic Remote

1. To start up the remote simply connect it to a power supply. This can be done via the Pico W’s micro usb power input adapter or by connecting the positive and negative terminals of a battery pack to the Vin and GND pads on the PCB.
2. Once powered, the remote will try to connect to the WiFi network and if successfully connected the remote will vibrate.
3. If something has gone wrong on startup the belt will vibrate three times. At this point, connect the Pico W to your laptop/PC and debug/run the code on Thonny to debug.

## Common Issues

**Uvicorn Command Not Working**

If executing the uvicorn command doesn’t work it may be because the location that uvicorn has been installed to may not be on the user’s PATH. To add to path follow the following steps:

1. Copy the directory path mentioned in the error message.
2. Search for “Environment Variables” in the start menu.
3. Click on “Edit the system environment variables”.
4. On “System properties” tab click the “Environment Variables” button.
5. In the “System Variables” section, scroll down and find the “PATH” variable.
6. Click the "Edit” button, “New” button, then paste the directory path from step 1.
7. Restart Command Prompt.