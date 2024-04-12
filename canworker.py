# Worker process for handling CAN data
# CAN controller is MCP25625 (Same as MCP2515)
# Received data is sent to the main process via a queue
# Data to be sent is received from the main process via a queue

# Useful documentation:
# https://python-can.readthedocs.io/en/stable/interfaces/socketcand.html
# https://python-can.readthedocs.io/en/stable/message.html
# https://forum.peak-system.com/viewtopic.php?t=1267
import can
import time
import RPi.GPIO
import subprocess

# MCP25625 pins
nRST_GPIO = 5
STBY_GPIO = 6
# GPIO 25: Interrupt

# Queues are passed to the worker process from the main process
rx_queue = None
tx_queue = None

# State dictionary is passed to the worker process from the main process
state = None

# CAN bus instance
bus = None

# CAN message format:
# Byte 0: Bit 0 - Drive button state
# Byte 0: Bit 1 - Neutral button state
# Byte 0: Bit 2 - Reverse button state
def build_message(drive_pressed, neutral_pressed, reverse_pressed):
    return can.Message(arbitration_id=0x102, data=[drive_pressed, neutral_pressed, reverse_pressed], extended_id=False)

def can_worker(_rx_queue, _tx_queue, _state):
    global rx_queue
    global tx_queue
    global state
    global bus

    rx_queue = _rx_queue
    tx_queue = _tx_queue

    # Configure GPIO for CAN controller and transceiver
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(nRST_GPIO, GPIO.OUT)
    GPIO.setup(STBY_GPIO, GPIO.OUT)

    # Set nRST high and STBY low
    GPIO.output(nRST_GPIO, GPIO.HIGH)
    GPIO.output(STBY_GPIO, GPIO.LOW)

    # Configure CAN interface
    try:
        # Run command 'ip link set can0 type can restart-ms 10 bitrate 500000'
        subprocess.run(['ip', 'link', 'set', 'can0', 'type', 'can', 'restart-ms', '10', 'bitrate', '500000'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to configure CAN interface")
        return
    
    # Bring up CAN interface
    try:
        # Run command 'ip link set up can0'
        subprocess.run(['ip', 'link', 'set', 'up', 'can0'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to bring up CAN interface")
        return

    # Main loop
    while True:
        # Initialize socketcan interface
        while bus is not None:
            try:
                bus = can.interface.Bus(bustype='socketcan', channel='can0')
                state['canconnected'] = True
            except:
                bus = None
                state['canconnected'] = False
                print("CAN initialization failed, retrying...")
                time.sleep(0.5)

        # Check if bus is in error state
        if bus.state == can.BusState.ERROR_ACTIVE:
            print("CAN bus is in error state")
            bus = None
            state['canconnected'] = False
            continue

        # Check for received data
        received = bus.recv(timeout=0.1)
        if (received is not None):
            rx_queue.put(received)

        # Check for data to send
        if not tx_queue.empty():
            msg = tx_queue.get()
            bus.send(msg)