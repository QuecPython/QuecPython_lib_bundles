'''
@Author: Stephen.Gao
@Date: 2022-03-31
@Description: OPT3001 sensor driver

Copyright 2022 - 2023 quectel
'''
from machine import I2C
import utime

I2C_ADDR = 0x44          #addr pin -GND
# I2C_ADDR = 0x45          #addr pin -VDD
# I2C_ADDR = 0x46          #addr pin -SDA
# I2C_ADDR = 0x47          #addr pin -SCL

#16bit register
I2C_LS_REG_RESULT = 0x00
I2C_LS_REG_CONFIG = 0x01
I2C_LS_REG_LOWLIMIT = 0x02
I2C_LS_REG_HIGHLIMIT = 0x03
I2C_LS_REG_MANUFACTURERID = 0x7E
I2C_LS_REG_DEVICEID = 0x7F

#common configuration
I2C_LS_CONFIG_DEFAULT = 0xc810          #shutdown
I2C_LS_CONFIG_SING_FULL_800MS = 0xca10  #single
I2C_LS_CONFIG_CONT_FULL_800MS = 0xcc10  #continuous

SHUT_DOWN_MODE = 0
ONT_SHOT_MODE = 1
CONTINU_MODE = 2

class Opt3001(object):
    def __init__(self,i2c,dev_addr=I2C_ADDR):
        self._i2c = i2c
        self._i2c_addr = dev_addr

        manu_id = self._read_data(I2C_LS_REG_MANUFACTURERID, 2)
        manu_id = (manu_id[0] << 8)  | manu_id[1]
        print(manu_id)
        if manu_id != 0x5449:
            raise Exception("OPT3001 manu id err.")

        self._write_data(I2C_LS_REG_CONFIG, [0xcc,0x10])
        utime.sleep_ms(15)
        print("sensor init complete.")

    def _write_data(self, reg, data):
        self._i2c.write(self._i2c_addr,
                        bytearray([reg]), len([reg]),
                        bytearray(data), len(data))
    def _read_data(self, reg, length):
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self._i2c.read(self._i2c_addr,
                             bytearray([reg]), len([reg]),
                             r_data, length,
                             0)
        return list(r_data)

    def set_measure_mode(self,mode=CONTINU_MODE):
        '''
        Set the measurement mode, continuous measurement and single measurement or shutdown
        :param mode: measurement mode 0-off 1-single 2-continuous
        :return: 0-success -1-mode wrong selection
        '''
        if mode not in range(3):
            return -1
        r_data = self._read_data(I2C_LS_REG_CONFIG, 2)
        r_data = (r_data[0] << 8) | r_data[1]
        print(r_data)
        w_data = (r_data & 0xf9ff) | (mode << 9)
        print(w_data)
        self._write_data(I2C_LS_REG_CONFIG, [(w_data >> 8), (w_data & 0xff)])
        utime.sleep_ms(20)
        return 0

    def read(self):
        '''
        The read value is converted into a lux value 
        please ensure that the measurement mode is not 0, otherwise it will get stuck
        @return: illuminance value，Unit:lux
        '''
        while 1:
            r_data = self._read_data(I2C_LS_REG_CONFIG, 2)[1]
            if (r_data & (1 << 7)):            #converted flag
                lux_ori = self._read_data(I2C_LS_REG_RESULT,2)
                lux_ori = (lux_ori[0] << 8) | lux_ori[1]
                #convert illuminance value
                mantisse = lux_ori & 0x0fff
                exponent = (lux_ori & 0xf000) >> 12
                lux = 2 ** exponent * mantisse * 0.01
                return lux