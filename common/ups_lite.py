import struct
import smbus

bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
I2C_ADDRESS = 0x36

def read_voltage():
    raw_value = bus.read_word_data(I2C_ADDRESS, 2)
    swapped = struct.unpack("<H", struct.pack(">H", raw_value))[0]
    voltage = swapped * 1.25 / 1000 / 16
    return voltage

def read_capacity():
    raw_value = bus.read_word_data(I2C_ADDRESS, 4)
    swapped = struct.unpack("<H", struct.pack(">H", raw_value))[0]
    capacity = swapped / 256
    return capacity
