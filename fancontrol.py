#!/usr/bin/env python3

import subprocess
import time
import os
import syslog

from gpiozero import OutputDevice


ON_THRESHOLD = 60   # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 50  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 17       # Which GPIO pin you're using to control the fan.


def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        syslog.syslog("Could not parse temperature output.")
        raise RuntimeError('Could not parse temperature output.')


if __name__ == '__main__':
    tmpThsOn = os.environ.get('FC_THS_ON')
    if (tmpThsOn != None):
        try:
            tmpThsOn = int(tmpThsOn)
            ON_THRESHOLD = tmpThsOn
        except:
            pass

    tmpThsOff = os.environ.get('FC_THS_OFF')
    if (tmpThsOff != None):
        try:
            tmpThsOff = int(tmpThsOff)
            OFF_THRESHOLD = tmpThsOff
        except:
            pass
        
    tmpSleep = os.environ.get('FC_SLEEP')
    if (tmpSleep != None):
        try:
            tmpSleep = int(tmpSleep)
            SLEEP_INTERVAL = tmpSleep
        except:
            pass
        
    tmpGpioP = os.environ.get('FC_GPIO_PIN')
    if (tmpGpioP != None):
        try:
            tmpGpioP = int(tmpGpioP)
            GPIO_PIN = tmpGpioP
        except:
            pass
        
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        syslog.syslog("OFF_THRESHOLD must be less than ON_THRESHOLD")
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    print("=============================")
    syslog.syslog("=============================")
    print("ON_THRESHOLD  : ", end = '')
    print(ON_THRESHOLD)
    syslog.syslog("ON_THRESHOLD  : " + str(ON_THRESHOLD))
    print("OFF_THRESHOLD : ", end = '')
    print(OFF_THRESHOLD)
    syslog.syslog("OFF_THRESHOLD : " + str(OFF_THRESHOLD))
    print("SLEEP_INTERVAL: ", end = '')
    print(SLEEP_INTERVAL)
    syslog.syslog("SLEEP_INTERVAL: " + str(SLEEP_INTERVAL))
    print("GPIO_PIN      : ", end = '')
    print(GPIO_PIN)
    syslog.syslog("GPIO_PIN      : " + str(GPIO_PIN))
    print("=============================")
    syslog.syslog("=============================")
    fan = OutputDevice(GPIO_PIN)

    while True:
        temp = get_temp()

        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        # print(temp)
        if temp > ON_THRESHOLD and not fan.value:
            print("accendo")
            syslog.syslog("ON")
            fan.on()

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < OFF_THRESHOLD:
            print("spengo")
            syslog.syslog("OFF")
            fan.off()

        time.sleep(SLEEP_INTERVAL)
