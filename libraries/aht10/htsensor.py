'''
File: i2c_sensor.py
Project: i2c
File Created: Monday, 28th December 2020 5:17:28 pm
Author: chengzhu.zhou
-----
Last Modified: Tuesday, 15th March 2022 1:50:35 pm
Modified By: Stephen.Gao
-----
Copyright 2022 - 2022 quectel
'''


from machine import I2C
import utime as time


class HtSensor(object):
    '''
    General class of temperature and humidity sensors
    '''
    def __init__(self,child):
        self._child=child

    def _write_data(self, reg, data):
        '''
        i2c write data
        '''
        self._child.i2c_dev.write(self._child.i2c_addre,
                           bytearray(reg), len(reg),
                           bytearray(data), len(data))

    def _read_data(self,reg, length):
        '''
        i2c read data
        '''
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self._child.i2c_dev.read(self._child.i2c_addre,
                          bytearray(reg), len(reg),
                          r_data, length,
                          0)
        return list(r_data)


    def ht_sensor_reset(self):
        '''
        reset
        '''
        self._write_data([self._child.AHT20_RESET_CMD],[])
        time.sleep_ms(20)  # at last 20ms
        print("reset complete. ")

    def _trigger_measure(self):
        '''
        Trigger measurement data conversion
        '''
        self._write_data([self._child.AHT20_START_MEASURMENT_CMD], [0x33, 0x00])
        time.sleep_ms(200)  # at last delay 75ms
        # check success or not
        r_data = self._read_data([],6)
        # check bit7
        if (r_data[0] >> 7) != 0x0:
            print("Conversion has error")
        else:
            return r_data[1:6]




