import machine
# import utime as time
import time

gpio_pin_number = 14
has_virtual_timers = False
# Define GPIO pin for pulse input
pulse_pin = machine.Pin(gpio_pin_number, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Dialing configuration constants in milliseconds
MAKE_DURATION_MS = 39       # Target make time (39 ms)
BREAK_DURATION_MS = 61      # Target break time (61 ms)
INTER_DIGIT_DELAY_MS = 500  # Minimum delay between digits (800 ms)
MAX_INTER_DIGIT_TIMEOUT_MS = 3000  # Maximum inter-digit timeout (3000 ms)

# Tolerance for signal variability (in ms)
TOLERANCE_MS = 10

# Define minimum and maximum allowable durations for MAKE and BREAK phases
MIN_MAKE_DURATION_MS = MAKE_DURATION_MS - TOLERANCE_MS
MAX_MAKE_DURATION_MS = MAKE_DURATION_MS + TOLERANCE_MS
MIN_BREAK_DURATION_MS = BREAK_DURATION_MS - TOLERANCE_MS
MAX_BREAK_DURATION_MS = BREAK_DURATION_MS + TOLERANCE_MS

# State definitions
STATE_IDLE = "idle"
STATE_MAKE = "make"
STATE_BREAK = "break"

# State machine variables
state = STATE_IDLE
ready_to_read = True
digit_pulses = 0
dialed_digits = []
last_pulse_time = time.ticks_ms()

# Timer for inter-digit delay
if has_virtual_timers:
    inter_digit_timer = machine.Timer(0)
    max_inter_digit_timer = machine.Timer(1)
else:
    inter_digit_timer = machine.Timer(-1)
    max_inter_digit_timer = machine.Timer(-1)




# Function to reset digit pulse count
def reset_digit():
    global digit_pulses
    digit_pulses = 0

# Timer callback for detecting inter-digit delay
def inter_digit_timeout(timer):
    global state, digit_pulses, dialed_digits
    
    if digit_pulses > 0:
        # If pulses counted, save as a digit and reset
        if digit_pulses == 10:
            digit_pulses = 0
        dialed_digits.append(digit_pulses)
        print("Digit dialed:", digit_pulses)
        reset_digit()
    
    state = STATE_IDLE  # Go back to idle state

# Timer callback for detecting max inter-digit timeout
def max_inter_digit_timeout(timer):
    global state, digit_pulses, dialed_digits, ready_to_read
    
    if digit_pulses > 0:
        # Finalize the last digit before resetting
        dialed_digits.append(digit_pulses)
        print("Finalizing digits due to max timeout:", digit_pulses)
        reset_digit()

    # Return to idle state
    state = STATE_IDLE
    ready_to_read = True

# Reset function to return to IDLE state and clear pulse count
def reset_to_idle():
    global state
    state = STATE_IDLE
    reset_digit()

# Interrupt handler for pulse input
def pulse_handler(pin):
    global last_pulse_time, state, digit_pulses, inter_digit_timer, max_inter_digit_timer, ready_to_read

    current_time = time.ticks_ms()
    pulse_duration_ms = time.ticks_diff(current_time, last_pulse_time)
    last_pulse_time = current_time  # Update the last pulse time
    ready_to_read = False

    if state == STATE_IDLE:
        if pin.value() == 1:  # Rising edge, start of MAKE phase
            state = STATE_MAKE
            inter_digit_timer.deinit()  # Cancel inter-digit timer
            max_inter_digit_timer.deinit()  # Cancel max timeout timer
        else:
            state = STATE_BREAK
            # inter_digit_timer.deinit()  # Cancel inter-digit timer
            # max_inter_digit_timer.deinit()  # Cancel max timeout timer


    elif state == STATE_MAKE:
        if pin.value() == 0:  # Falling edge, start of BREAK phase
            if MIN_MAKE_DURATION_MS <= pulse_duration_ms <= MAX_MAKE_DURATION_MS:
                state = STATE_BREAK
                # Reset or start inter-digit timer
                inter_digit_timer.init(period=INTER_DIGIT_DELAY_MS, mode=machine.Timer.ONE_SHOT, callback=inter_digit_timeout)
                max_inter_digit_timer.init(period=MAX_INTER_DIGIT_TIMEOUT_MS, mode=machine.Timer.ONE_SHOT, callback=max_inter_digit_timeout)
            else:
                # print("Ignoring out-of-range make duration and resetting to IDLE" + str(pulse_duration_ms))
                # reset_to_idle()
                state = STATE_BREAK

    elif state == STATE_BREAK:
        if pin.value() == 1:  # Rising edge, start of next MAKE phase
            if MIN_BREAK_DURATION_MS <= pulse_duration_ms <= MAX_BREAK_DURATION_MS:
                digit_pulses += 1
                state = STATE_MAKE
                # Reset or start inter-digit timer
                inter_digit_timer.init(period=INTER_DIGIT_DELAY_MS, mode=machine.Timer.ONE_SHOT, callback=inter_digit_timeout)
                max_inter_digit_timer.init(period=MAX_INTER_DIGIT_TIMEOUT_MS, mode=machine.Timer.ONE_SHOT, callback=max_inter_digit_timeout)
            else:
                print("Ignoring out-of-range break duration and resetting to IDLE")
                reset_to_idle()



# Function to check if a full phone number has been dialed
def retrieve_dialed_number():
    global dialed_digits
    if ready_to_read and state == STATE_IDLE and len(dialed_digits) > 0:
        # Retrieve and clear the dialed digits
        phone_number = '-'.join(map(str, dialed_digits))
        dialed_digits = []  # Reset the array for the next number
        return phone_number
    return None


# Attach interrupt to the pulse pin
pulse_pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=pulse_handler)
if __name__ == '__main__':
    # Main loop to monitor and retrieve phone numbers
    while True:
        # Check periodically for a completed phone number
        dialed_number = retrieve_dialed_number()
        if dialed_number:
            print("Detected dialed phone number:", dialed_number)
        
        # Sleep for a bit to avoid excessive polling
        time.sleep(0.1)
