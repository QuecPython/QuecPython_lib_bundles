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
File: i2c_ltr_303als.py
Project: i2c
File Created: Thursday, 10th March 2022 3:55:22 pm
Author: elian.wang

-----
Copyright 2022 - 2022 quectel
'''

from machine import ExtInt
from machine import I2C
#from machine import I2C_simulation
import utime as time
from machine import ExtInt


class itl_303als():
    i2c_log = None
    i2c_dev = None
    i2c_addre = 0x29

    IRQ_RISING = 0
    IRQ_FALLING = 1

    light_value = [0, 0]
    # ALS operation mode control SW reset
    CONTR_ADDR = 0x80
    # ALS measurement rate in active mode
    MEAS_RATE_ADDR = 0x85
    # ALS measurement CH1 data, lower byte
    DATA_CH1_LOW_ADDR = 0x88
    # ALS measurement CH1 data, upper byte
    DATA_CH1_HIGH_ADDR = 0x89
    DATA_CH0_LOW_ADDR = 0x8A
    DATA_CH0_HIGH_ADDR = 0x8B
    # ALS new data status
    STATUS_ADDR = 0x8C
    # Interrupt settings
    INTERRUPT_ADDR = 0x8F
    # ALS interrupt upper threshold, lower byte
    THRES_UP_LOW_ADDR = 0x97
    # ALS interrupt upper threshold, upper byte
    THRES_UP_HIGH_ADDR = 0x98
    INTERRUPT_PERSIST_ADDR = 0x9E

    def __init__(self, GPIOn, threshod, user_cb, intr_output_mode=IRQ_RISING):
        self.cb = user_cb
        self.up_threshod = threshod
        #self.i2c_log = log.getLogger(Alise)
        self.i2c_dev = I2C(I2C.I2C0, I2C.FAST_MODE)  # 返回i2c对象
        
        if intr_output_mode == 0:
            self.extint = ExtInt(GPIOn, ExtInt.IRQ_RISING , ExtInt.PULL_DISABLE , self.ext_cb)
            # Enable Interrupt,INT pin is considered active when it is a logic 1
            print('INTERRUPT_ADDR: {}'.format([0x0E]))
            self._write([self.INTERRUPT_ADDR], [0x0E])
           
        elif intr_output_mode == 1:
            self.extint = ExtInt(GPIOn, ExtInt.IRQ_FALLING , ExtInt.PULL_PU , self.ext_cb)
            # Enable Interrupt,INT pin is considered active when it is a logic 0
            print('INTERRUPT_ADDR: {}'.format([0x0A]))
            self._write([self.INTERRUPT_ADDR], [0x0A])
        else:
            raise Exception('set gpio trigger mode fault')
        self.extint.enable()        
        # Enable ALS
        self._write([self.CONTR_ADDR], [0x01])
        time.sleep_ms(20)  # at last 10ms
        
        # Set ALS Integration Time 200ms, Repeat Rate 200ms
        self._write([self.MEAS_RATE_ADDR], [0x12])
        # Setthe upper limit of the interrupt threshold value 0x5DC 
        self._write([self.THRES_UP_LOW_ADDR], [self.up_threshod])
        self._write([self.THRES_UP_HIGH_ADDR], [self.up_threshod >> 8])
        # 10 consecutive ALS values out of threshold range
        self._write([self.INTERRUPT_PERSIST_ADDR], [0x0A])

    def _write(self, reg_addr, data):
        ret = self.i2c_dev.write(self.i2c_addre,
                           bytearray(reg_addr), 1,
                           bytearray(data), len(data))
        print('ret: {}'.format(ret))

    def _read(self, reg_addr, length):
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self.i2c_dev.read(self.i2c_addre,
                            bytearray(reg_addr), 1,
                            r_data, length,
                            0)
        if ret == -1:
            return []
        else:
            return list(r_data)

    def ext_cb(self, args):
        self.cb(self.read())

    def reset(self):
        self._write([self.CONTR_ADDR], [0x02])
        time.sleep_ms(20)  # at last 20ms

    def read(self):
        # Judge ALS data valid
        als_sta = self._read([self.STATUS_ADDR], 1)
        if len(als_sta) != 0 and (als_sta[0] & 0x80 == 0):
            data0 = self._read([self.DATA_CH1_LOW_ADDR], 1)
            data1 = self._read([self.DATA_CH1_HIGH_ADDR], 1)
            data2 = self._read([self.DATA_CH0_LOW_ADDR], 1)
            data3 = self._read([self.DATA_CH0_HIGH_ADDR], 1)
            if len(data0) != 0 and len(data1) != 0 and len(data2) != 0 and len(data3) != 0:
                self.light_value[0] = (data1[0] << 8) | data0[0]
                self.light_value[1] = (data3[0] << 8) | data2[0]
                return self.light_value
            else:
                return []
        else:
            return []

def user_cb_test(light):
    print('light over interrupt  {}'.format(light))

if __name__ == "__main__":
    # GPIO32  GPIO8
    als_dev = itl_303als(ExtInt.GPIO32, 100, user_cb_test, intr_output_mode=itl_303als.IRQ_FALLING)
    for i in range(20):
        print("test 1 ",i)
        print("read data:", als_dev.read())
        time.sleep(1)

