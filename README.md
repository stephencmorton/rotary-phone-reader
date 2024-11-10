# rotary-phone-reader
**Micropython** code for your embedded project to read dialled numbers from a rotary phone. Use an old phone as an input device for your retro-futuristic project.

I designed this for an ESP32 board, but I think any board that is supported by the micropython `machine` module will work.

This code is interrupt-driven so your main program is free to do whatever you want. You can poll for a dialed number, or register a callback to run once a number is dialed.

## Installation

Copy this to your `/lib/` folder and you're ready to go.

_This has no dependencies beyond `machine` and `time` that are already part of micropython._

## Getting Started

Sample programs:

*polling*

```python
import time
from pulse_decoder import retrieve_dialed_number, gpio_pin_number

gpio_pin_number = 14
def main():
    while True:
        # Check periodically for a completed phone number
        dialed_number = retrieve_dialed_number()
        if dialed_number:
            print("Detected dialed phone number:", dialed_number)
            if dialed_number[0] == 1:
                # 1 - ABC - Play ABBA
                pass
            elif dialed_number[0] == 2:
                # 2- DEF - Play Debussy
                pass
            elif dialed_number == (8,6,7,5,3,0,9):
                # Play Tommy Tutone "867-5309/Jenny"
                pass

        # Sleep for a bit to avoid excessive polling
        time.sleep(0.1)
```

*interrupt-driven*

```python
import time
from pulse_decoder import register_callback, gpio_pin_number

gpio_pin_number = 14

def dialed_number_callback(dialed_number):
    if dialed_number:
        print("Detected dialed phone number:", dialed_number)
        if dialed_number[0] == 1:
            # 1 - ABC - Play ABBA
            pass
        elif dialed_number[0] == 2:
            # 2 - DEF - Play Debussy
            pass
        elif dialed_number == (8,6,7,5,3,0,9):
            # Play Tommy Tutone "867-5309/Jenny"
            pass

def main():
    # do some stuff
    register_callback(dialed_number_callback)
    # do more stuff
```


## Configurable items

- `gpio_pin_number` - integer - Which ESP32 GPIO pin you want to use. Must support an internal pull-up resistor.
- `virtual_timers` - boolean -  Whether your device supports virtual timers. (default `False`. The ESP32 does not.) The program will choose timers 0, and 1. You can change those too, if you want.
- Various pulse characteristics if you really want `*DURATION*`, `*DELAY*`, `*TIMEOUT*`, `*TOLERANCE*`. But you should not have to touch them.

## Debugging
This should "just work", but if your specific phone's characteristics are different from those expected, you may need to tweak the code a little. There are commented-out print statements you can uncomment to 
(To make the code as fast as possible in interrupt-context, these are left as commented rather than if-statements.)

## Further Reading
### References
- https://en.wikipedia.org/wiki/Pulse_dialing
- https://www.dialogic.com/webhelp/csp1010/8.4.1_ipn3/dev_overview_dsp_one_-_e1_dial_pulse_address_signaling.htm
- https://www.3amsystems.com/World_Tone_Database/Signalling_guide?q=Pulse_dialing


### Installing micropython modules on your ESP32

From the REPL:
```python
import os
os.mkdir "lib" # Just once

import mip
mip.install("xmltok") # For example
```

### Unit testing

There is no unit testing. It's so hardware-dependent that I never Mock-ed it all up. Just load it on your ESP32 and test.
