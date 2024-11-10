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

