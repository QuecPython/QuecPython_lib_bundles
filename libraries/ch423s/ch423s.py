'''
@Author: Stephen.Gao
@Date: 2022-04-6
@Description: GH423S IO ex driver

Copyright 2022 - 2022 quectel
'''
from machine import Pin
import utime

GPIO_IN = 0
GPIO_OUT = 1

#次i2c设备没有地址
#每个cmd就是一个地址

CH423_SYS_CMD = 0x48        #系统参数命令地址
BIT_X_INT = 0x08            #使能输入电平变化中断，为0禁止输入电平变化中断；为1并且DEC_H为0允许输出电平变化中断
BIT_DEC_H = 0x04            #控制开漏输出引脚高8位的片选译码
BIT_DEC_L = 0x02            #控制开漏输出引脚低8位的片选译码
BIT_IO_OE = 0x01            #gpio引脚的输出使能，为1允许输出
BIT_OD_EN = 0x10            #使能输出引脚 OC15～OC0 的开漏输出

CH423_OC_L_CMD = 0x44       #设置低 8 位通用输出命令（默认模式推挽）
BIT_OC0_L_DAT = 0x01        #OC0为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC1_L_DAT = 0x02        #OC1为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC2_L_DAT = 0x04        #OC2为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC3_L_DAT = 0x08        #OC3为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC4_L_DAT = 0x10        #OC4为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC5_L_DAT = 0x20        #OC5为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC6_L_DAT = 0x40        #OC6为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）
BIT_OC7_L_DAT = 0x80        #OC7为0则使引脚输出低电平，为1则引脚输出高电平（开漏不输出）

CH423_OC_H_CMD = 0x46       #设置高 8 位通用输出命令

CH423_SET_IO_CMD = 0x60     #设置双向输入输出命令

CH423_RD_IO_CMD = 0x4D      #读取双向输入输出命令


class Ch423s(object):
    def __init__(self,clk,dio):
        self._pin_dio = dio
        self._pin_clk = clk
        self._clk = Pin(clk, Pin.OUT, Pin.PULL_DISABLE, 1)
        self._dio = Pin(dio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self._write_reg(CH423_SYS_CMD,0x00) #设置系统参数命令

    def delay_ms(self, ms):
        utime.sleep_ms(ms)

    def delay_us(self, num):
        pass

    def _start_signal(self):
        self._dio = Pin(self._pin_dio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self._dio.write(1)
        self._clk.write(1)
        self.delay_us(5)
        self._dio.write(0)
        self.delay_us(5)
        self._clk.write(0)
        self.delay_us(5)

    def _stop_signal(self):
        self._dio = Pin(self._pin_dio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self._clk.write(0)
        self.delay_us(2)
        self._dio.write(0)
        self.delay_us(2)
        self._clk.write(1)
        self.delay_us(2)
        self._dio.write(1)
        self.delay_us(2)

    def ack(self, is_ack):
        self._dio = Pin(self._pin_dio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self._dio.write(is_ack)
        self.delay_us(2)
        self._clk.write(1)
        self.delay_us(4)
        self._clk.write(0)

    def _wait_ack(self):
        i = 0
        self._clk.write(0)
        self.delay_us(2)
        self._dio = Pin(self._pin_dio, Pin.IN, Pin.PULL_DISABLE, 1)
        self.delay_us(2)

        while (self._dio.read()):
            i += 1
            if i > 2000:
                # self._stop_signal()
                print('iic stop')
                self._clk.write(0)
                self._dio = Pin(self._pin_dio, Pin.OUT, Pin.PULL_DISABLE, 1)
                return 1
        self.delay_us(2)
        self._clk.write(1)
        self.delay_us(2)
        self._clk.write(0)
        # self.delay_us(2)
        return 0

    def _write_byte(self, data):
        self._dio = Pin(self._pin_dio, Pin.OUT, Pin.PULL_DISABLE, 1)
        for j in range(0, 8):
            self._clk.write(0)
            self.delay_us(2)
            # 从高位开始发
            if data & 0x80:
                self._dio.write(1)
            else:
                self._dio.write(0)
            data <<= 1
            self.delay_us(2)
            self._clk.write(1)
            self.delay_us(2)
        self._clk.write(0)
        self._wait_ack()
        # print("#")

    def _read_byte(self):
        # self._dio = Pin(RDADIO, Pin.IN, Pin.PULL_DISABLE, 1)
        self._dio = Pin(self._pin_dio, Pin.IN, Pin.PULL_DISABLE, 1)
        recive = 0
        utime.sleep_ms(12)
        for i in range(0, 8):
            recive <<= 1
            self._clk.write(0)
            self.delay_us(2)
            self._clk.write(1)
            self.delay_us(2)
            level = self._dio.read()
            if level == 1:
                recive |= 1
        self._clk.write(0)
        self.ack(1)
        return recive

    def _read_reg(self, cmd):
        self._start_signal()
        self._write_byte(cmd)
        r_data = self._read_byte()
        self._stop_signal()
        return r_data

    def _write_reg(self, cmd, val):
        self._start_signal()
        self._write_byte(cmd)
        self._write_byte(val)
        self._stop_signal()

    def reset(self):
        self._write_reg(CH423_SYS_CMD, 0x00)

    def config(self,dir=GPIO_IN,int=0,odr=0):
        '''
        配置双向输入输出引脚 IO7～IO0的输出使能 ，
        IO_OE输入电平变化中断使能 X_INT，
        输出引脚 OC15～OC0 开漏输出使能 OD_EN
        :param dir: gpio方向
        :param int: 输入电平变化中断使能
        :param odr: 开漏输出使能
        '''
        if dir not in (0,1) or int not in (0,1) or odr not in (0,1):
            return -1
        w_byte = 0x00
        if dir:
            w_byte = w_byte | BIT_IO_OE
        if int:
            w_byte = w_byte | BIT_X_INT
        if odr:
            w_byte = w_byte | BIT_OD_EN
        self._write_reg(CH423_SYS_CMD, w_byte)
        return 0

    def gpio_pin(self, pin, value=1):
        '''
        确保是输出模式，gpio引脚设置
        :param pin: 引脚号: 0-7
        :param value: 0 or 1
        '''
        if pin not in range(8) or value not in (0,1):
            return -1
        r_byte = self.read_gpio()
        if value:
            bit_io = 1 << pin
            w_byte = r_byte | bit_io
        else:
            bit_io = 1 << pin
            w_byte = r_byte & ~bit_io
        self._write_reg(CH423_SET_IO_CMD, w_byte)
        return 0

    def gpo_h(self,value):
        '''
        通用输出高8位整体设值
        :param value: 高八位电平高低
        '''
        if value not in range(256):
            return -1
        self._write_reg(CH423_OC_H_CMD, value)
        return 0

    def gpo_l(self,value):
        '''
        通用输出低8位整体设值
        :param value: 低八位电平高低
        '''
        if value not in range(256):
            return -1
        self._write_reg(CH423_OC_L_CMD, value)
        return 0

    def gpio(self,value):
        '''
        确保是输出模式，gpio 8位整体设值
        :param value: 八位电平高低
        '''
        if value not in range(256):
            return -1
        self._write_reg(CH423_SET_IO_CMD, value)
        return 0

    def read_gpio(self):
        '''
        读取 IO7～IO0 引脚的当前状态
        :return: 当 IO_OE 为 0 时为获取输入状态，否则为获取输出状态
        '''
        r_byte = self._read_reg(CH423_RD_IO_CMD)
        return r_byte

if __name__ == "__main__":
    ch423 = Ch423s(Pin.GPIO12,Pin.GPIO13)
    print("init success. ")
    utime.sleep(1)
    #ch423.config(odr=1)
    # for i in range(10):
    #     ch423.gpo_h(0x00)
    #     utime.sleep(0.1)
    #     ch423.gpo_h(0x01)
    #     utime.sleep(0.1)
    ch423.config(dir=1)
    print("gpio all set output.")
    for i in range(10):
        # ch423.gpio(0xff)
        ch423.gpio_pin(pin=5,value=1)
        utime.sleep(0.1)
        print(ch423.read_gpio())
        ch423.gpio(0x00)
        utime.sleep(0.1)
        print(ch423.read_gpio())