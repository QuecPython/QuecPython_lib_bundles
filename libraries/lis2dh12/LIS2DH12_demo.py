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
@Date: 2023-03-22
@Description: LIS2DH12 sensor demo

Copyright 2022 - 2023 quectel
'''

import utime
from machine import I2C
from machine import ExtInt
from usr.LIS2DH12 import lis2dh12

LIS2DH12_OUT_X_L = 0x28
LIS2DH12_OUT_X_H = 0x29
LIS2DH12_OUT_Y_L = 0x2A
LIS2DH12_OUT_Y_H = 0x2B
LIS2DH12_OUT_Z_L = 0x2C
LIS2DH12_OUT_Z_H = 0x2D
LIS2DH12_FIFO_CTRL_REG = 0x2E

# control register
LIS2DH12_CTRL_REG1 = 0x20
LIS2DH12_CTRL_REG2 = 0x21
LIS2DH12_CTRL_REG3 = 0x22
LIS2DH12_CTRL_REG4 = 0x23
LIS2DH12_CTRL_REG5 = 0x24
LIS2DH12_CTRL_REG6 = 0x25
LIS2DH12_REFERENCE_REG = 0x26
LIS2DH12_STATUS_REG = 0x27

# status register
LIS2DH12_STATUS_REG_AUX = 0x7

# interrupt register
LIS2DH12_INT1_CFG = 0x30
LIS2DH12_INT1_SRC = 0x31
LIS2DH12_INT1_THS = 0x32
LIS2DH12_INT1_DURATION = 0x33

LIS2DH12_INT2_CFG = 0x34
LIS2DH12_INT2_SRC = 0x35
LIS2DH12_INT2_THS = 0x36
LIS2DH12_INT2_DURATION = 0x37

LIS2DH12_WHO_AM_I = 0x0F

LIS2DH12_CLICK_CFG = 0x38
LIS2DH12_CLICK_SRC = 0x39
LIS2DH12_CLICK_THS = 0x3A
LIS2DH12_TIME_LIMIT = 0x3B
LIS2DH12_TIME_LATENCY = 0x3C
LIS2DH12_TIME_WINDOW = 0x3D

STANDARD_GRAVITY = 9.806

# types of interrupt
# single click
X_SINGLE_CLICK_INT = 0x01
Y_SINGLE_CLICK_INT = 0x04
Z_SINGLE_CLICK_INT = 0x10
XYZ_SINGLE_CLICK_INT = 0x15
# double click
X_DOUBLE_CLICK_INT = 0x02
Y_DOUBLE_CLICK_INT = 0x08
Z_DOUBLE_CLICK_INT = 0x20
XYZ_DOUBLE_CLICK_INT = 0x2A
# move int
POSI_CHANGE_RECOGNIZE = 0xFF
X_POSI_CHANGE_RECOGNIZE = 0x83
Y_POSI_CHANGE_RECOGNIZE = 0x8C
Z_POSI_CHANGE_RECOGNIZE = 0xB0
MOVE_RECOGNIZE = 0x7F
X_MOVE_RECOGNIZE = 0x03
Y_MOVE_RECOGNIZE = 0x0C
Z_MOVE_RECOGNIZE = 0x30
# free fall int
FF_RECOGNIZE = 0x95  #and zl yl xl


def int_cb(args):
    print('click just happened...')
    acc = dev.int_processing_data()
    print("read_acceleration result: ", acc)


if __name__ == "__main__":
    # initialize i2c
    i2c_dev = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    # initialize the lis2dh12 object
    dev = lis2dh12(i2c_dev, 14)
    # enable single_click_interrupt
    dev.int_enable(XYZ_SINGLE_CLICK_INT)
    # set interrupt callback
    dev.set_int_callback(int_cb)
    # start sensor
    dev.start_sensor()
    # LP mode
    dev.set_mode(2)

    print("interrupt detecting...")


