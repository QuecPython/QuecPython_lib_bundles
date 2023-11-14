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

# register addresses in port=0, bank=1 mode (easier maths to convert)
_MCP_IOCON_DEFAULT = 0x0A    # R/W Configuration Register 初始为0x0A

_MCP_IODIR        = 0x00    # R/W I/O Direction Register
_MCP_IPOL         = 0x01    # R/W Input Polarity Port Register
_MCP_GPINTEN      = 0x02    # R/W Interrupt-on-Change Pins
_MCP_DEFVAL       = 0x03    # R/W Default Value Register
_MCP_INTCON       = 0x04    # R/W Interrupt-on-Change Control Register
_MCP_IOCON        = 0x05    # R/W Configuration Register
_MCP_GPPU         = 0x06    # R/W Pull-Up Resistor Register
_MCP_INTF         = 0x07    # R   Interrupt Flag Register (read clears)
_MCP_INTCAP       = 0x08    # R   Interrupt Captured Value For Port Register
_MCP_GPIO         = 0x09    # R/W General Purpose I/O Port Register
_MCP_OLAT         = 0x0a    # R/W Output Latch Register

# Config register (IOCON) bits
_MCP_IOCON_INTPOL = 2
_MCP_IOCON_ODR    = 4
# _MCP_IOCON_HAEN = 8 # no used - for spi flavour of this chip
_MCP_IOCON_DISSLW = 16
_MCP_IOCON_SEQOP  = 32
_MCP_IOCON_MIRROR = 64
_MCP_IOCON_BANK   = 128


class Port():
    # 表示两个8位端口之一
    def __init__(self, port, mcp):
        self._port = port & 1  # 0=PortA, 1=PortB
        self._mcp = mcp

    def _which_reg(self, reg):
        if self._mcp._config & 0x80 == 0x80:
            # bank = 1
            return reg | (self._port << 4)
        else:
            # bank = 0
            return (reg << 1) + self._port

    def _flip_property_bit(self, reg, condition, bit):
        if condition:
            setattr(self, reg, getattr(self, reg) | bit)
        else:
            setattr(self, reg, getattr(self, reg) & ~bit)

    def _read(self, reg):
        r_data = bytearray(1)
        self._mcp._i2c.read(self._mcp._address, bytearray([self._which_reg(reg)]),1 , r_data, 1, 0)
        return list(r_data)[0]
        #return self._mcp._i2c.readfrom_mem(self._mcp._address, self._which_reg(reg), 1)[0]

    def _write(self, reg, val):
        val &= 0xff
        self._mcp._i2c.write(self._mcp._address, bytearray([self._which_reg(reg)]), 1, bytearray([val]),1)
        #self._mcp._i2c.writeto_mem(self._mcp._address, self._which_reg(reg), bytearray([val]))
        # if writing to the config register, make a copy in mcp so that it knows
        # which bank you're using for subsequent writes
        if reg == _MCP_IOCON:
            self._mcp._config = val

    @property
    def mode(self):
        return self._read(_MCP_IODIR)
    @mode.setter
    def mode(self, val):
        self._write(_MCP_IODIR, val)

    @property
    def input_polarity(self):
        return self._read(_MCP_IPOL)
    @input_polarity.setter
    def input_polarity(self, val):
        self._write(_MCP_IPOL, val)

    @property
    def interrupt_enable(self):
        return self._read(_MCP_GPINTEN)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self._write(_MCP_GPINTEN, val)

    @property
    def default_value(self):
        return self._read(_MCP_DEFVAL)
    @default_value.setter
    def default_value(self, val):
        self._write(_MCP_DEFVAL, val)

    @property
    def interrupt_compare_default(self):
        return self._read(_MCP_INTCON)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self._write(_MCP_INTCON, val)

    @property
    def io_config(self):
        return self._read(_MCP_IOCON)
    @io_config.setter
    def io_config(self, val):
        self._write(_MCP_IOCON, val)

    @property
    def pullup(self):
        return self._read(_MCP_GPPU)
    @pullup.setter
    def pullup(self, val):
        self._write(_MCP_GPPU, val)

    # read only
    @property
    def interrupt_flag(self):
        return self._read(_MCP_INTF)

    # read only
    @property
    def interrupt_captured(self):
        return self._read(_MCP_INTCAP)

    @property
    def gpio(self):
        return self._read(_MCP_GPIO)
    @gpio.setter
    def gpio(self, val):
        # writing to this register modifies the OLAT register for pins configured as output
        self._write(_MCP_GPIO, val)

    @property
    def output_latch(self):
        '''
        输出锁存器
        '''
        return self._read(_MCP_OLAT)
    @output_latch.setter
    def output_latch(self, val):
        # modifies the output latches on pins configured as outputs
        self._write(_MCP_OLAT, val)


class Mcp23017():
    def __init__(self, i2c, address=0x20, bank=1):
        self._i2c = i2c
        self._address = address
        self._config = 0x00
        self._virtual_pins = {}
        if self._i2c.write(self._address, bytearray([0x05]), 1, bytearray([0]), 1) == -1:
            raise OSError('MCP23017 not found at I2C address {0}'.format(self._address))

        if bank == 1:
            #往IOCON.bank写入bank,如果没找到i2c从设备地址
            self._i2c.write(self._address, bytearray([_MCP_IOCON_DEFAULT]), 1, bytearray([_MCP_IOCON_BANK]), 1)
        self.init(bank)

    def init(self,bank):

        self.porta = Port(0, self)
        self.portb = Port(1, self)

        self.io_config = 0x00      # io expander configuration - same on both ports, only need to write once

        # Reset to all inputs with no pull-ups and no inverted polarity.
        self.porta.mode = 0xFF                       # in/out direction (0=out, 1=in)
        self.portb.mode = 0xFF
        self.porta.input_polarity = 0x00             # 反转端口输入极性 (0=normal, 1=invert)
        self.portb.input_polarity = 0x00
        self.porta.interrupt_enable = 0x00           # int on change pins (0=disabled, 1=enabled)
        self.portb.interrupt_enable = 0x00
        self.porta.default_value = 0x00              # default value for int on change
        self.portb.default_value = 0x00
        self.porta.interrupt_compare_default = 0x00  # int on change control (0=compare to prev val, 1=compare to def val)
        self.portb.interrupt_compare_default = 0x00
        self.pullup = 0x0000                     # gpio weak pull up resistor - when configured as input (0=disabled, 1=enabled)
        self.gpio = 0x0000                       # port (0=logic low, 1=logic high)

        print(self.porta.mode,self.portb.mode)    #0xFF
        print(self.porta.interrupt_enable,self.portb.interrupt_enable)   #0x00
        print(self.porta.gpio,self.portb.gpio)                      #0x00

    def config(self, interrupt_polarity=None, interrupt_open_drain=None, sda_slew=None, sequential_operation=None, interrupt_mirror=None, bank=None):
        io_config = self.porta.io_config

        if interrupt_polarity is not None:
            # 将INT配置为push-pull
            # 0: 低电平有效
            # 1: 高电平有效
            io_config = self._flip_bit(io_config, interrupt_polarity, _MCP_IOCON_INTPOL)
            if interrupt_polarity:
                # 如果设置为1，则取消ODR位 - interrupt_open_drain
                interrupt_open_drain = False
        if interrupt_open_drain is not None:
            # configure INT as open drain, overriding interrupt_polarity
            # 0: INTPOL sets the polarity
            # 1: Open drain, INTPOL ignored
            io_config = self._flip_bit(io_config, interrupt_open_drain, _MCP_IOCON_ODR)
        if sda_slew is not None:
            # 0: SDA引脚上的回转率功能已启用
            # 1: SDA引脚上的回转率功能已关闭
            io_config = self._flip_bit(io_config, sda_slew, _MCP_IOCON_DISSLW)
        if sequential_operation is not None:
            # 0: 启用，地址指针增量
            # 1: 禁用，地址指针已修复
            io_config = self._flip_bit(io_config, sequential_operation, _MCP_IOCON_SEQOP)
        if interrupt_mirror is not None:
            # 0: Independent INTA,INTB pins
            # 1: Internally linked INTA,INTB pins
            io_config = self._flip_bit(io_config, interrupt_mirror, _MCP_IOCON_MIRROR)
        if bank is not None:
            # 0: 寄存器在A和B端口之间交替
            # 1: 首先注册所有端口A，然后注册所有端口B
            io_config = self._flip_bit(io_config, bank, _MCP_IOCON_BANK)

        # both ports share the same register, so you only need to write on one
        self.porta.io_config = io_config
        self._config = io_config

    def _flip_bit(self, value, condition, bit):
        if condition:
            value |= bit
        else:
            value &= ~bit
        return value

    def pin(self, pin, mode=None, value=None, pullup=None, polarity=None, interrupt_enable=None, interrupt_compare_default=None, default_value=None):
        assert 0 <= pin <= 15
        port = self.portb if pin // 8 else self.porta
        bit = (1 << (pin % 8))
        if mode is not None:
            # 0: Pin is configured as an output
            # 1: Pin is configured as an input
            port._flip_property_bit('mode', mode & 1, bit)
        if value is not None:
            # 0: 引脚设置为逻辑低
            # 1: 引脚设置为逻辑高
            port._flip_property_bit('gpio', value & 1, bit)
        if pullup is not None:
            # 0: 弱上拉100k欧姆电阻器禁用
            # 1: 弱上拉100k欧姆电阻器启用
            port._flip_property_bit('pullup', pullup & 1, bit)
        if polarity is not None:
            # 0: GPIO寄存器位反映输入引脚的相同逻辑状态
            # 1: GPIO寄存器位反映输入引脚的相反逻辑状态
            port._flip_property_bit('input_polarity', polarity & 1, bit)
        if interrupt_enable is not None:
            # 0: Disables GPIO input pin for interrupt-on-change event
            # 1: Enables GPIO input pin for interrupt-on-change event
            port._flip_property_bit('interrupt_enable', interrupt_enable & 1, bit)
        if interrupt_compare_default is not None:
            # 0: Pin value is compared against the previous pin value
            # 1: Pin value is compared against the associated bit in the DEFVAL register
            port._flip_property_bit('interrupt_compare_default', interrupt_compare_default & 1, bit)
        if default_value is not None:
            # 0: Default value for comparison in interrupt, when configured to compare against DEFVAL register
            # 1: Default value for comparison in interrupt, when configured to compare against DEFVAL register
            port._flip_property_bit('default_value', default_value & 1, bit)
        if value is None:
            return port.gpio & bit == bit

    def interrupt_triggered_gpio(self, port):
        # 哪个gpio触发了中断
        # only 1 bit will be set
        port = self.portb if port else self.porta
        return port.interrupt_flag

    def interrupt_captured_gpio(self, port):
        # 中断时捕获的gpio值
        # 读取此信息将清除当前中断
        port = self.portb if port else self.porta
        return port.interrupt_captured

    # mode (IODIR register)
    @property
    def mode(self):
        return self.porta.mode | (self.portb.mode << 8)
    @mode.setter
    def mode(self, val):
        self.porta.mode = val
        self.portb.mode = (val >> 8)

    # input_polarity (IPOL register)
    @property
    def input_polarity(self):
        return self.porta.input_polarity | (self.portb.input_polarity << 8)
    @input_polarity.setter
    def input_polarity(self, val):
        self.porta.input_polarity = val
        self.portb.input_polarity = (val >> 8)

    # interrupt_enable (GPINTEN register)
    @property
    def interrupt_enable(self):
        return self.porta.interrupt_enable | (self.portb.interrupt_enable << 8)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self.porta.interrupt_enable = val
        self.portb.interrupt_enable = (val >> 8)

    # default_value (DEFVAL register)
    @property
    def default_value(self):
        return self.porta.default_value | (self.portb.default_value << 8)
    @default_value.setter
    def default_value(self, val):
        self.porta.default_value = val
        self.portb.default_value = (val >> 8)

    # interrupt_compare_default (INTCON register)
    @property
    def interrupt_compare_default(self):
        return self.porta.interrupt_compare_default | (self.portb.interrupt_compare_default << 8)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self.porta.interrupt_compare_default = val
        self.portb.interrupt_compare_default = (val >> 8)

    # io_config (IOCON register)
    # This register is duplicated in each port. Changing one changes both.
    @property
    def io_config(self):
        return self.porta.io_config
    @io_config.setter
    def io_config(self, val):
        self.porta.io_config = val

    # pullup (GPPU register)
    @property
    def pullup(self):
        return self.porta.pullup | (self.portb.pullup << 8)
    @pullup.setter
    def pullup(self, val):
        self.porta.pullup = val
        self.portb.pullup = (val >> 8)

    # interrupt_flag (INTF register)
    # read only
    @property
    def interrupt_flag(self):
        return self.porta.interrupt_flag | (self.portb.interrupt_flag << 8)

    # interrupt_captured (INTCAP register)
    # read only
    @property
    def interrupt_captured(self):
        return self.porta.interrupt_captured | (self.portb.interrupt_captured << 8)

    # gpio (GPIO register)
    @property
    def gpio(self):
        return self.porta.gpio | (self.portb.gpio << 8)
    @gpio.setter
    def gpio(self, val):
        self.porta.gpio = val
        self.portb.gpio = (val >> 8)

    # output_latch (OLAT register)
    @property
    def output_latch(self):
        return self.porta.output_latch | (self.portb.output_latch << 8)
    @output_latch.setter
    def output_latch(self, val):
        self.porta.output_latch = val
        self.portb.output_latch = (val >> 8)

    # list interface
    # mcp[pin] lazy creates a VirtualPin(pin, port)
    def __getitem__(self, pin):
        assert 0 <= pin <= 15
        if not pin in self._virtual_pins:
            self._virtual_pins[pin] = VirtualPin(pin, self.portb if pin // 8 else self.porta)
        return self._virtual_pins[pin]

class VirtualPin():
    def __init__(self, pin, port):
        self._pin = pin % 8
        self._bit = 1 << self._pin
        self._port = port

    def _flip_bit(self, value, condition):
        return value | self._bit if condition else value & ~self._bit

    def _get_bit(self, value):
        return (value & self._bit) >> self._pin

    def value(self, val=None):
        # if val, write, else read
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)
        else:
            return self._get_bit(self._port.gpio)

    def input(self, pull=None):
        # if pull, enable pull up, else read
        self._port.mode = self._flip_bit(self._port.mode, 1) # mode = input
        if pull is not None:
            self._port.pullup = self._flip_bit(self._port.pullup, pull & 1) # toggle pull up

    def output(self, val=None):
        # if val, write, else read
        self._port.mode = self._flip_bit(self._port.mode, 0) # mode = output
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)