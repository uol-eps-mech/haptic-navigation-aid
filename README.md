# Haptic Navigation Aid

## Setting Up Your Development Environment

### Cloning the GitHub Repository

In order to access all the code and files you need to first clone the GitHub repository. To do this ensure you have `git` installed. Then open a terminal and navigate to the folder you want the repository to be cloned and execute the command:

`git clone https://github.com/uol-eps-mech/haptic-navigation-aid.git`

### Install Thonny

Thonny is the IDE you will be using to run/debug code on the Pico Ws. For instructions on how to use Thonny or setup a new Pico W using Thonny refer to:

```
https://projects.raspberrypi.org/en/projects/get-started-pico-w
```

### Install all dependencies

**\*\***API**\*\***

-   To be able to start up the **API** you need to have `fastapi` installed (`uvicorn` is installed with fastapi).
    -   This can be done by executing `pip install fastpi`
-   For the localisation module to work you need:
    -   pyserial to be installed: `pip install pyserial`
    -   For a windows PC to recognise the DWM1001 tag you need J-Link drivers to be installed this can be done via this url:
        -   https://www.segger.com/downloads/jlink/JLink_Windows_V788j_x86_64.exe
        -   Ensure that once the drivers are installed you can see a J-Link device connected under `Devices and Printers` in the control panel.

**\*\*\*\***Belt**\*\*\*\***

The Pico W on the belt requires the `picozero` package to be installed. This can be done via Thonny through the `manage packages` option under the `Tools` menu.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5f293ab3-1d93-4340-985a-94bbda7c794a/Untitled.png)

Make sure to have the Pico W selected in the bottom right corner:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/6e3f2808-8555-42b6-b531-d665d17c39b3/Untitled.png)

****\*\*\*\*****Remote****\*\*\*\*****

The Pico W on the remote also requires the `picozero` package to be installed. This can be done as shown above.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e7e85069-1e2b-441f-a446-fe1451edd564/Untitled.png)

## Starting up the Device:

In order to turn the device on there are four main steps:

### Haptic Belt

1. Ensure that you are facing towards the right as per the map stored in `map.py`
2. Connect the Pico W to the power supply.
3. Once the Pico W has connected to the WiFi network the belt will vibrate twice and the LED on board the Pico W will turn on.
4. If something has gone wrong on startup the belt will vibrate three times. At this point, connect the Pico W to your laptop/PC and debug/run the code on Thonny to debug.
    1. If this issue is that it isn’t connecting to the WiFi network, try disconnecting the power supply and reconnecting it to the Pico W.

The belt is now active.

### Web API

1. To start up the web API simply open a terminal, navigate to the folder `haptic-navigation-aid` or the root folder if it is called something else.
2. Execute the command `uvicorn apiv2:app --host 0.0.0.0 --reload`

Let’s understand this command better. `uvicorn` is what we use to start up the server/api. It needs to know which file the api sits in and what the name of the FastAPI object variable is. Hence why we specify `apiv2` which is the name of the file `[apiv2.py](http://apiv2.py)` followed by a `:` and then the name of the FastAPI object variable `app` as seen in the code:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/95d5441e-e05d-4b68-ac4f-f54c13e8c2b3/Untitled.png)

Following this we specify a few requirements. Firstly, we set the `--host` flag to `0.0.0.0` which tell uvicorn to host the API on `[localhost](http://localhost)`. Secondly, we set the `--reload` flag, this should be used during debugging only as it reloads the API every time a change to any dependency is made i.e. any file used by the API. This makes the development process much quicker but should be turned off during demos/trials.

### Haptic Remote

1. To start up the remote simply connect it to a power supply. This can be done via the Pico W’s micro usb power input adapter or by connecting the positive and negative terminals of a battery pack to the Vin and GND pads on the PCB.
2. Once powered, the remote will try to connect to the WiFi network and if successfully connected the remote will vibrate.
3. If something has gone wrong on startup the belt will vibrate three times. At this point, connect the Pico W to your laptop/PC and debug/run the code on Thonny to debug.

## License

This work is licensed under the [MIT license](LICENSE).

© 2023, University of Leeds.

The authors, Kaif Kutchwala, Thomas Green and Raymond Holt, have asserted their moral rights.
