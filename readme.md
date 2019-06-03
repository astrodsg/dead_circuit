# Circuit Python Projects!

I got my hands on a [HalloWing M0 Express](https://circuitpython.org/board/hallowing_m0_express/) and then played around with some projects. 


[Circuit Python Getting Tutorial](https://learn.adafruit.com/welcome-to-circuitpython)


# Getting Started

I created a bunch of little examples that can be deployed. All the examples have a folder in `projects`. Basically, the files in that folder are copied to the CIRCUITPY mounted usb which can then execute the script and run. 


## 1) Attached Device

First thing to do is attach the device to the computer by the USB drive. 


## 2) Copy files to Device

I created a helper script to: 1) erase the current files 2) copy all necessary files to the device. It works like this:


```
python deploy.py [project_name]
```

The device reboots and will then run the code.py script. 


## 3) Interact with running device

If you want to interact with it from the terminal 


```
ls /dev/tty.* | grep usb
screen /dev/tty.usbmodem14201
```

See a [cheat sheet on screen](http://aperiodic.net/screen/quick_reference) for more instructions.


## 4) Modify the code

Use a text editor like Sublime Text to modeify the code.py file to your liking.


Take note of [editor specific considerations](https://learn.adafruit.com/welcome-to-circuitpython/creating-and-editing-code)


Also note: I used `watchdog` python library to create a `watcher.py` script. Run this by typing:

```
python watcher.py [project_name]

```

Then whenever a file change is saved (like the code.py file) within the project directory (e.g. projects/hello_world/code.py) that file will be copied to the CIRCUITPY drive and the device will automatically reboot and use it. 








