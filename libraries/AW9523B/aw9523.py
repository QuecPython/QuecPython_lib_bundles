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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file      :aw9523.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2023-02-01 09:21:44
@copyright :Copyright (c) 2022
"""

from queue import Queue
from machine import ExtInt
from usr.logging import Logger
from usr.common import create_thread

log = Logger(__name__)


_AW9523_DEFAULT_ADDR_KEY = (0x58)  # The key drive address is 0x58, and the IO extension address is 0x5B
_AW9523_DEFAULT_ADDR_IO = (0x5B)
_AW9523_REG_CHIPID = (0x10)  # Register for hardcode chip ID
_AW9523_REG_SOFTRESET = (0x7F)  # Register for soft resetting
_AW9523_REG_INTENABLE0 = (0x06)  # Register for enabling interrupt
_AW9523_REG_GCR = (0x11)  # Register for general configuration
_AW9523_REG_LEDMODE = (0x12)  # Register for configuring  current
_AW9523_REG_INPUT0 = (0x00)  # Register for reading input values
_AW9523_REG_OUTPUT0 = (0x02)  # Register for writing output values
_AW9523_REG_CONFIG0 = (0x04)  # Register for configuring direction


class Port():
    # 表示两个8位端口之一
    def __init__(self, port, aw):
        self._port = port & 1  # 0=PortA, 1=PortB
        self._aw = aw

    def _which_reg(self, reg):
            return reg + self._port

    def _flip_property_bit(self, reg, condition, bit):
        if condition:
            setattr(self, reg, getattr(self, reg) | bit)
        else:
            setattr(self, reg, getattr(self, reg) & ~bit)

    def _read(self, reg):
        r_data = bytearray(1)
        self._aw._i2c.read(self._aw._address, bytearray([self._which_reg(reg)]), 1, r_data, 1, 0)
        return list(r_data)[0]

    def _write(self, reg, val):
        val &= 0xff
        self._aw._i2c.write(self._aw._address, bytearray([self._which_reg(reg)]), 1, bytearray([val]), 1)

    @property
    def mode(self):
        return self._read(_AW9523_REG_CONFIG0)

    @mode.setter
    def mode(self, val):
        self._write(_AW9523_REG_CONFIG0, val)

    @property
    def interrupt_enable(self):
        return self._read(_AW9523_REG_INTENABLE0)

    @interrupt_enable.setter
    def interrupt_enable(self, val):
        # log.debug("val:",bin(val))
        self._write(_AW9523_REG_INTENABLE0, val)

    # read only
    @property
    def interrupt_flag(self):
        return self._read(_AW9523_REG_INPUT0)

    @property
    def gpio(self):
        return self._read(_AW9523_REG_OUTPUT0)

    @gpio.setter
    def gpio(self, val):
        # writing to this register modifies the OLAT register for pins configured as output
        self._write(_AW9523_REG_OUTPUT0, val)


class AW9523:

    # _pin_to_addr = ([0x24 + pin for pin in range(8)] +
    #                 [0x20 + pin - 8 for pin in range(8, 12)] +
    #                 [0x2C + pin - 12 for pin in range(12, 16)])

    def __init__(self, i2c_bus, int_pin=1, int_mode=0, int_callback=None, address=_AW9523_DEFAULT_ADDR_KEY):
        self._i2c = i2c_bus
        self._int_pin = int_pin
        self._int_mode = int_mode
        self._address = address
        self._int_callback = int_callback
        self.__ext_thread_id = None
        self.__ext_queue = Queue()
        self._ret = 0x001F   # 接收电平状态

        if self._address == _AW9523_DEFAULT_ADDR_KEY:
            self._extint = ExtInt(self._int_pin, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.__extfun)
            self._extint.enable()
            self.__ext_thread_id = create_thread(self.__extfun_thread, stack_size=0x4000)

        # Read device ID.  AW9523B ID read default value is 23H
        self.read_buf = bytearray(5)
        self._i2c.read(address, bytearray((_AW9523_REG_CHIPID, 0xff)), 1, self.read_buf, 1, 20)
        # log.debug("read_buff:", self.read_buf)
        if (self.read_buf[0] != 0x23):
            raise AttributeError("Cannot find a AW9523")

        # self.reset()
        self.porta = Port(0, self)
        self.portb = Port(1, self)

    def __extfun(self, args):
        self.__ext_queue.put(args)

    #执行中断回调
    def __extfun_thread(self):
        while 1:
            args = self.__ext_queue.get()
            log.debug('### interrupt  {} ###'.format(args))
            # 读取两组电平，判断触发了中断的io,中断信号前后电平对比
            # status_0 = self._read(_AW9523_REG_INPUT0)
            # status_1 = self._read(_AW9523_REG_INPUT0 + 1)
            self._i2c.read(_AW9523_DEFAULT_ADDR_KEY, bytearray((_AW9523_REG_INPUT0, 0xff)), 1, self.read_buf, 1, 20)
            status_0 = self.read_buf[0]
            self._i2c.read(_AW9523_DEFAULT_ADDR_KEY, bytearray((_AW9523_REG_INPUT0 + 1, 0xff)), 1, self.read_buf, 1, 20)
            status_1 = self.read_buf[0]
            status = (status_1 << 8) | status_0
            # log.debug('### io level {} ###'.format(bin(status)))

            change = (self._ret ^ status)
            if self._int_callback is None:
                return

            #byte 引脚号 pin_level 电平
            if change is not 0:
                byte = 0
                pin_level = 1
                while byte < 16:
                    if (change & (1 << byte)):
                        break
                    else:
                        byte = byte + 1

                if (status & (1 << byte)):
                    pin_level = 1
                else:
                    pin_level = 0

                #判断是否该IO是否中断使能
                # flag_0 = self._read(_AW9523_REG_INTENABLE0)
                # flag_1 = self._read(_AW9523_REG_INTENABLE0 + 1)
                self._i2c.read(_AW9523_DEFAULT_ADDR_KEY, bytearray((_AW9523_REG_INTENABLE0, 0xff)), 1, self.read_buf, 1, 20)
                flag_0 = self.read_buf[0]
                self._i2c.read(_AW9523_DEFAULT_ADDR_KEY, bytearray((_AW9523_REG_INTENABLE0 + 1, 0xff)), 1, self.read_buf, 1, 20)
                flag_1 = self.read_buf[0]
                flag = (flag_1 << 8) | flag_0
                if flag & (1 << byte) == 0:
                    list_push = [byte, pin_level]
                    self._int_callback(list_push)
                # log.debug('### io level {} ###'.format(bin(status)))
            # 保存上一次电平状态
            self._ret = status

    def _read(self, addr):
        r_data = bytearray(1)
        self._i2c.read(self._address, bytearray([addr]), 1, r_data, 1, 20)
        return list(r_data)[0]

    def _write(self, addr, *vals):
        # log.debug("write vals:", vals)
        self._i2c.write(self._address, bytearray([addr]), 1, bytearray(list(vals)), len(list(vals)))

    def reset(self):
        self._write(_AW9523_REG_SOFTRESET, 0x00)  # 对该寄存器写 00H 复位 reset
        self._write(_AW9523_REG_GCR, 0b00010000)  # pushpull output    D[4]=0,Open-Drain模式; D[4]=1,Push-Pull模式
        self._write(_AW9523_REG_INTENABLE0, 0xff, 0xff)  # no IRQ  0-中断使能； 1-中断不使能
        self._write(_AW9523_REG_INTENABLE0 + 1, 0xff, 0xff)  # no IRQ
        # self._write(_AW9523_REG_LEDMODE, 0xff, 0xff)  #gpio mode
        # self._write(_AW9523_REG_LEDMODE+1, 0xff, 0xff)  #gpio mode

    # set aw9523 pin
    def pin(self, pin, mode=None, value=None, interrupt_enable=None):
        assert 0 <= pin <= 15
        port = self.portb if pin // 8 else self.porta
        bit = (1 << (pin % 8))
        if mode is not None:
            # 0: Pin is configured as an output
            # 1: Pin is configured as an input
            port._flip_property_bit('mode', mode & 1, bit)
        if value is not None:
            # 0: 引脚设置为逻辑低电平
            # 1: 引脚设置为逻辑高电平
            port._flip_property_bit('gpio', value & 1, bit)
        if interrupt_enable is not None:
            # 1: Disables GPIO input pin for interrupt-on-change event
            # 0: Enables GPIO input pin for interrupt-on-change event
            if interrupt_enable == 0:
                interrupt_enable = 1
            else:
                interrupt_enable = 0
            port._flip_property_bit('interrupt_enable', interrupt_enable & 1, bit)
        if value is None:
            return port.gpio & bit == bit

    # mode (IODIR register)
    @property
    def mode(self):
        return self.porta.mode | (self.portb.mode << 8)

    @mode.setter
    def mode(self, val):
        self.porta.mode = val
        self.portb.mode = (val >> 8)

    # interrupt_enable (GPINTEN register)
    @property
    def interrupt_enable(self):
        return self.porta.interrupt_enable | (self.portb.interrupt_enable << 8)

    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self.porta.interrupt_enable = val
        self.portb.interrupt_enable = (val >> 8)

    # interrupt_flag (INTF register)
    # read only
    @property
    def interrupt_flag(self):
        return self.porta.interrupt_flag | (self.portb.interrupt_flag << 8)

    # gpio (GPIO register)
    @property
    def gpio(self):
        return self.porta.gpio | (self.portb.gpio << 8)

    @gpio.setter
    def gpio(self, val):
        self.porta.gpio = val
        self.portb.gpio = (val >> 8)

    # 获取引脚电平，pin为引脚号0~15
    def read(self, pin):
        status_0 = self._read(_AW9523_REG_INPUT0)
        status_1 = self._read(_AW9523_REG_INPUT0 + 1)
        status = (status_1 << 8) | status_0
        pin_level = 0
        if (status & (1 << pin)):
            pin_level = 1
        else:
            pin_level = 0
        return pin_level
