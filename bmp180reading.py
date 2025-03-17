from machine import Pin, I2C
import time
import struct

class BMP180:
    def __init__(self, i2c, addr=0x77):
        self.i2c = i2c
        self.addr = addr
        self.calibration = self._read_calibration_data()

    def _read_bytes(self, reg, nbytes):
        self.i2c.writeto(self.addr, bytes([reg]))
        return self.i2c.readfrom(self.addr, nbytes)

    def _write_byte(self, reg, value):
        self.i2c.writeto(self.addr, bytes([reg, value]))

    def _read_calibration_data(self):
        calibration = {}
        calibration['AC1'] = struct.unpack('>h', self._read_bytes(0xAA, 2))[0]
        calibration['AC2'] = struct.unpack('>h', self._read_bytes(0xAC, 2))[0]
        calibration['AC3'] = struct.unpack('>h', self._read_bytes(0xAE, 2))[0]
        calibration['AC4'] = struct.unpack('>H', self._read_bytes(0xB0, 2))[0]
        calibration['AC5'] = struct.unpack('>H', self._read_bytes(0xB2, 2))[0]
        calibration['AC6'] = struct.unpack('>H', self._read_bytes(0xB4, 2))[0]
        calibration['B1'] = struct.unpack('>h', self._read_bytes(0xB6, 2))[0]
        calibration['B2'] = struct.unpack('>h', self._read_bytes(0xB8, 2))[0]
        calibration['MB'] = struct.unpack('>h', self._read_bytes(0xBA, 2))[0]
        calibration['MC'] = struct.unpack('>h', self._read_bytes(0xBC, 2))[0]
        calibration['MD'] = struct.unpack('>h', self._read_bytes(0xBE, 2))[0]
        return calibration

    def read_temperature(self):
        self._write_byte(0xF4, 0x2E)  
        time.sleep(0.005)
        raw_temp = struct.unpack('>H', self._read_bytes(0xF6, 2))[0]
        X1 = ((raw_temp - self.calibration['AC6']) * self.calibration['AC5']) >> 15
        X2 = (self.calibration['MC'] << 11) // (X1 + self.calibration['MD'])
        B5 = X1 + X2
        temperature = (B5 + 8) >> 4
        return temperature / 10.0

    def read_pressure(self):
        self._write_byte(0xF4, 0x34)  
        time.sleep(0.005)
        raw_pressure = struct.unpack('>H', self._read_bytes(0xF6, 2))[0]
        return raw_pressure

    def read_altitude(self, sea_level_pressure=101325):
        pressure = self.read_pressure()
        altitude = 44330 * (1 - (pressure / sea_level_pressure) ** (1 / 5.255))
        return altitude
