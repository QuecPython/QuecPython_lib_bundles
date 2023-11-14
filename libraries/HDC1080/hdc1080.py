# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
@Author: Stephen.Gao
@Date: 2022-04-06
@Description: HDC1080 sensor driver

Copyright 2022 - 2022 quectel
'''
from machine import I2C
import utime as time

# I2C Address
HDC1080_ADDRESS =                       0x40    # 1000000 
# Registers
HDC1080_TEMPERATURE_REGISTER =          0x00
HDC1080_HUMIDITY_REGISTER =             0x01
HDC1080_CONFIGURATION_REGISTER =        0x02
HDC1080_MANUFACTURERID_REGISTER =       0xFE
HDC1080_DEVICEID_REGISTER =         0xFF
HDC1080_SERIALIDHIGH_REGISTER =         0xFB
HDC1080_SERIALIDMID_REGISTER =          0xFC
HDC1080_SERIALIDBOTTOM_REGISTER =       0xFD


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo=ErrorInfo

    def __str__(self):
        return self.errorinfo


class Hdc1080(object):
    '''
    HDC1080 class
    '''
    def __init__(self,i2c,addr=HDC1080_ADDRESS):
        self._i2c = i2c
        self._i2c_addr = addr

        time.sleep_ms(15)
        manu_id = self._read_data(HDC1080_MANUFACTURERID_REGISTER,2)
        manu_id = (manu_id[0] << 8) | manu_id[1]
        # print(manu_id)
        if manu_id != 0x5449:
            raise CustomError("HDC1080 manu id err.")

        self._write_data(HDC1080_CONFIGURATION_REGISTER,[0x10,0x00])
        time.sleep_ms(15)
        print("sensor init complete.")

    def _write_data(self, reg, data):
        '''
        i2c write data
        '''
        self._i2c.write(self._i2c_addr,
                           bytearray([reg]), len([reg]),
                           bytearray(data), len(data))

    def _read_data(self,reg, length):
        '''
        i2c read data
        '''
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self._i2c.read(self._i2c_addr,
                          bytearray([reg]), len([reg]),
                          r_data, length,
                          0)
        return list(r_data)

    def _read_data_delay(self,reg, length):
        '''
        i2c read data with delay
        '''
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self._i2c.read(self._i2c_addr,
                          bytearray([reg]), len([reg]),
                          r_data, length,
                          50)
        return list(r_data)

    def reset(self):
        self._write_data(HDC1080_CONFIGURATION_REGISTER, [0x10, 0x00])

    def read_temperature(self):
        tem_data = self._read_data_delay(HDC1080_TEMPERATURE_REGISTER,2)
        tem_data = (tem_data[0] << 8) | tem_data[1]
        tem = (tem_data / 65536) * 165 - 40
        return tem

    def read_humidity(self):
        hum_data = self._read_data_delay(HDC1080_HUMIDITY_REGISTER,2)
        hum_data = (hum_data[0] << 8) | hum_data[1]
        hum = (hum_data / 65536) * 100
        return hum

    def read(self):
        tem = self.read_temperature()
        time.sleep_ms(15)
        hum = self.read_humidity()
        return (hum,tem)
