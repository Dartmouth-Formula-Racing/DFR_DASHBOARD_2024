import multiprocessing
import queue
import time
# import RPi.GPIO as GPIO

# import canworker
import webworker

ANIMATE = True

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

    # var faults_elm = document.getElementById('faults');
    # var bot_elm = document.getElementById('bot');
    # var brb_elm = document.getElementById('brb');
    # var imd_elm = document.getElementById('imd');
    # var bms_elm = document.getElementById('bms');
    # var tsms_elm = document.getElementById('tsms');
    # var drive_state_elm = document.getElementById('drive_state');

    # var acctemp_elm = document.getElementById('acctemp');
    # var leftinvtemp_elm = document.getElementById('leftinvtemp');
    # var rightinvtemp_elm = document.getElementById('rightinvtemp');

    # var throttlebar_elm = document.getElementById('throttlebar');
    # var throttleval_elm = document.getElementById('throttleval');

    # var rpm_elm = document.getElementById('rpm');
    # var speed_elm = document.getElementById('speed');
    # var lap_elm = document.getElementById('lap');
    # var laptime_elm = document.getElementById('laptime');

    # var batterybar_elm = document.getElementById('batterybar');
    # var batteryval_elm = document.getElementById('batteryval');

    state['bot'] = False
    state['brb'] = False
    state['imd'] = False
    state['bms'] = False
    state['tsms'] = False
    state['drive_state'] = 'NEUTRAL'
    state['acctemp'] = 150.0
    state['leftinvtemp'] = 150.0
    state['rightinvtemp'] = 150.0
    state['throttle_position'] = 50.0
    state['rpm'] = 5500.0
    state['speed'] = 50.0
    state['lap'] = 0
    state['laptime'] = 0.0
    state['battery_percentage'] = 50.0
    state['accumulator_voltage'] = 250.0
    state['LV_voltage'] = 50.0
    state['accumulator_current'] = 150.0
    state['accumulator_temperature'] = 150.0
    state['estimated_range'] = 150.0
    state['tractioncontrol'] = True
    state['mileage'] = 1000.0
    state['temperaturesok'] = True

    web_process = multiprocessing.Process(target=webworker.run, args=(state,), daemon=True)
    # can_process = multiprocessing.Process(target=canworker.can_worker, args=(rx_queue, tx_queue), daemon=True)
    web_process.start()
    # can_process.start()


    increase = True

    while True:
        if ANIMATE:

            # Simulate data
            if increase:
                state['bot'] = True
                state['brb'] = False
                state['imd'] = True
                state['bms'] = False
                state['tsms'] = True
                state['drive_state'] = 'REVERSE'
                state['acctemp'] -= 1
                state['leftinvtemp'] += 1
                state['rightinvtemp'] -= 1
                state['throttle_position'] += 1
                state['rpm'] -= 10
                state['speed'] += 1.0
                state['lap'] -= 1
                state['laptime'] += 1.0
                state['battery_percentage'] -= 1
                state['accumulator_voltage'] += 1
                state['LV_voltage'] -= 1
                state['accumulator_current'] += 1
                state['accumulator_temperature'] -= 1
                state['estimated_range'] += 1
                state['tractioncontrol'] = False
                state['mileage'] += 1.0
                state['temperaturesok'] = False
            else:
                state['bot'] = False
                state['brb'] = True
                state['imd'] = False
                state['bms'] = True
                state['tsms'] = False
                state['drive_state'] = 'DRIVE'
                state['acctemp'] += 1
                state['leftinvtemp'] -= 1
                state['rightinvtemp'] += 1
                state['throttle_position'] -= 1
                state['rpm'] += 10
                state['speed'] -= 1.0
                state['lap'] += 1
                state['laptime'] -= 1.0
                state['battery_percentage'] += 1
                state['accumulator_voltage'] -= 1
                state['LV_voltage'] += 1
                state['accumulator_current'] -= 1
                state['accumulator_temperature'] += 1
                state['estimated_range'] -= 1
                state['tractioncontrol'] = True
                state['mileage'] -= 1.0
                state['temperaturesok'] = True
            if state['speed'] >= 100:
                increase = False
            elif state['speed'] <= 0:
                increase = True
            time.sleep(1/100)
        else:
            state['bot'] = True
            state['brb'] = True
            state['imd'] = True
            state['bms'] = True
            state['tsms'] = True
            state['drive_state'] = 'DRIVE'
            state['acctemp'] = 100
            state['leftinvtemp'] = 100
            state['rightinvtemp'] = 100
            state['throttle_position'] = 100
            state['rpm'] = 100
            state['speed'] = 100
            state['lap'] = 100
            state['laptime'] = 100
            state['battery_percentage'] = 100
            state['accumulator_voltage'] = 100
            state['LV_voltage'] = 100
            state['accumulator_current'] = 100
            state['accumulator_temperature'] = 100
            state['estimated_range'] = 100
            state['tractioncontrol'] = True
            state['mileage'] = 100
            state['temperaturesok'] = True

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
