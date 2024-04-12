import multiprocessing
import queue
import time
# import RPi.GPIO as GPIO

# import canworker
import webworker

DRIVE_BUTTON_GPIO = 17
DRIVE_LED_GPIO = 27
NEUTRAL_BUTTON_GPIO = 24
NEUTRAL_LED_GPIO = 25
REVERSE_BUTTON_GPIO = 22
REVERSE_LED_GPIO = 23

if __name__ == '__main__':
    # Set up GPIO
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(DRIVE_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(DRIVE_LED_GPIO, GPIO.OUT)
    # GPIO.setup(NEUTRAL_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(NEUTRAL_LED_GPIO, GPIO.OUT)
    # GPIO.setup(REVERSE_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(REVERSE_LED_GPIO, GPIO.OUT)

    drive_pressed = False
    neutral_pressed = False
    reverse_pressed = False

    rx_queue = multiprocessing.Queue()
    tx_queue = multiprocessing.Queue()
    
    manager = multiprocessing.Manager()

    # Create a shared dictionary to store the data
    state = manager.dict()

    state['bot'] = False
    state['brb'] = False
    state['imd'] = False
    state['bms'] = False
    state['tsms'] = False
    state['drive_state'] = 'NEUTRAL'
    state['acctemp'] = 0.0
    state['leftinvtemp'] = 0.0
    state['rightinvtemp'] = 0.0
    state['throttle_position'] = 0.0
    state['rpm'] = 0.0
    state['speed'] = 0.0
    state['lap'] = 0
    state['laptime'] = 0.0
    state['battery_percentage'] = 0.0
    state['accumulator_voltage'] = 0.0
    state['LV_voltage'] = 0.0
    state['accumulator_current'] = 0.0
    state['accumulator_temperature'] = 0.0
    state['estimated_range'] = 0.0
    state['tractioncontrol'] = False
    state['mileage'] = 0.0
    state['temperaturesok'] = False
    state['canconnected'] = False

    web_process = multiprocessing.Process(target=webworker.run, args=(state,), daemon=True)
    # can_process = multiprocessing.Process(target=canworker.can_worker, args=(rx_queue, tx_queue, state,), daemon=True)
    web_process.start()
    # can_process.start()

    while True:
        # Check button states
        # if GPIO.input(DRIVE_BUTTON_GPIO) == 0:
        #     drive_pressed = True
        # else:
        #     drive_pressed = False
        # if GPIO.input(NEUTRAL_BUTTON_GPIO) == 0:
        #     neutral_pressed = True
        # else:
        #     neutral_pressed = False
        # if GPIO.input(REVERSE_BUTTON_GPIO) == 0:
        #     reverse_pressed = True
        # else:
        #     reverse_pressed = False

        # Build CAN message
        # msg = canworker.build_message(drive_pressed, neutral_pressed, reverse_pressed)

        # Add status message to the TX queue
        # tx_queue.put(msg)

        # Process RX queue messages
        while not rx_queue.empty():
            msg = rx_queue.get()
            if msg == None:
                continue
            if msg.arbitration_id == 0x100:
                state['speed'] = msg.data[0]
            elif msg.arbitration_id == 0x101:
                state['accumulator_voltage'] = msg.data[0]
                state['LV_voltage'] = msg.data[1]
            else:
                print(f"Unknown message received: {msg}")

    # Wait for processes to finish
    web_process.join()
    # can_process.join()
