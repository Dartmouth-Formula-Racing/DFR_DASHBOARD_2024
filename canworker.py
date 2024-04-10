# Worker process for handling CAN data
# CAN controller is MCP25625 (Same as MCP2515)
# Received data is sent to the main process via a queue
# Data to be sent is received from the main process via a queue

# Useful documentation:
# https://python-can.readthedocs.io/en/stable/interfaces/socketcand.html
# https://python-can.readthedocs.io/en/stable/message.html
import can

# Queues are passed to the worker process from the main process
rx_queue = None
tx_queue = None

# Initialize CAN controller
bus = can.interface.Bus(channel='can0', bustype='socketcan')


# CAN message format:
# Byte 0: Bit 0 - Drive button state
# Byte 0: Bit 1 - Neutral button state
# Byte 0: Bit 2 - Reverse button state
def build_message(drive_pressed, neutral_pressed, reverse_pressed):
    return can.Message(arbitration_id=0x102, data=[drive_pressed, neutral_pressed, reverse_pressed], extended_id=False)

def can_worker(_rx_queue, _tx_queue):
    global rx_queue
    global tx_queue

    rx_queue = _rx_queue
    tx_queue = _tx_queue

    while True:
        # Check for received data
        if bus.recv():
            rx_queue.put(bus.recv())

        # Check for data to send
        if not tx_queue.empty():
            msg = tx_queue.get()
            bus.send(msg)