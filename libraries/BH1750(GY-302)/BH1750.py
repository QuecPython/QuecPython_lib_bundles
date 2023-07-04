'''
@Author: Stephen.Gao
@Date: 2022-03-31
@Description: BH1750（GY302） sensor driver

Copyright 2022 - 2022 quectel
'''
import utime
from machine import I2C

#oprecode
POWER_DOWN = 0X00
POWER_ON = 0X01
RESET = 0X07

#mode type
CONTI_H_MODE = 0X10  #1lx精度
CONTI_H_MODE2 = 0X11 #0.5lx精度
CONTI_L_MODE = 0X13  #4lx精度
ONE_H_MODE = 0X20
ONE_H_MODE2 = 0X21
ONE_L_MODE = 0X23

class Bh1750(object):
    '''
    bh1750(gy302) class
    API：on(),off(),reset(),set_measure_mode(mode),read()
    '''
    def __init__(self,i2c,dev_addr=0x23):
        self._i2c = i2c
        self._dev_addr = dev_addr
        self._i2c.write(self._dev_addr, bytearray([0x00]), 1, bytearray(0), 0)

    def on(self):
        '''
        switch on the sensor
        '''
        self._i2c.write(self._dev_addr,bytearray([POWER_ON]),1,bytearray(0),0)
        utime.sleep_ms(50)

    def off(self):
        '''
        inactive state
        '''
        self._i2c.write(self._dev_addr, bytearray([POWER_DOWN]), 1, bytearray(0), 0)

    def reset(self):
        '''
        reset the sensor
        '''
        self._i2c.write(self._dev_addr,bytearray([RESET]),1,bytearray(0),0)
        utime.sleep_ms(50)

    def set_measure_mode(self,mode=CONTI_H_MODE2):
        '''
        Set measurement mode, continuous measurement and single measurement, with different accuracies
        :param mode: measurement mode
        '''
        self._i2c.write(self._dev_addr, bytearray([mode]), 1, bytearray(0), 0)
        utime.sleep_ms(180)

    def read(self):
        '''
        Read the illumination value in lux
        :return: illumination value in lux
        '''
        origin_data = bytearray(2)
        self._i2c.read(self._dev_addr, bytearray(0), 0, origin_data, 2, 10)
        origin_data = list(origin_data)
        trans_data = origin_data[0]
        trans_data = (trans_data << 8) + origin_data[1]
        lux = trans_data // 1.2

        return int(lux)
