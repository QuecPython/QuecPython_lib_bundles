'''
@Author: Stephen.Gao
@Date: 2022-03-31
@Description: bl0939 driver

Copyright 2022 - 2022 quectel
'''
from machine import SPI
from usr.common_except import CustomError
import utime

#寄存器地址 只读
IA_FAST_RMS = 0X00  #A快速有效值 无符号
IA_WAVE = 0x01      #A通道电流波形寄存器 有符号
IB_WAVE = 0x02      #B通道电流波形寄存器 有符号
V_WAVE = 0x03       #电压波形寄存器 有符号
IA_RMS = 0X04       #A电流有效值 无符号
IB_RMS = 0X05       #B电流有效值 无符号
V_RMS = 0X06        #电压有效值 无符号
IB_FAST_RMS = 0X07  #B快速有效值
A_WATT = 0X08       #A通道有功功率
B_WATT = 0X09       #B通道有功功率

#寄存器地址 读写
IA_FAST_RMS_CTRL = 0x10     #A通道快速有效值控制寄存器
MODE = 0x18                 #用户模式选择寄存器
SOFT_RESET = 0x19           #写入0x5A5A5A时，用户区寄存器复位
USR_WRPROT = 0x1A           #用户写保护寄存器
TPS_CTRL = 0x1B             #温度模式控制寄存器
IB_FAST_RMS_CTRL = 0x1E     #B通道快速有效值控制寄存器


class Bl0939(object):
    '''
    Bl0939计量芯片类
    开放接口：read()
    '''
    def __init__(self, port=1, mode=1, clk=0):
        self._spi = SPI(port, mode, clk)
        self._write_reg(SOFT_RESET, 0x5a5a5a)


    def _read_reg(self,reg):
        '''
        spi读数据
        :param reg: 要读的寄存器
        :return: 读出的三字节数据
        '''
        w_data = bytearray([0x55,reg,0xff,0xff,0xff,0xff])
        r_data = bytearray(6)

        if self._spi.write_read(r_data, w_data, 6) == -1:
            raise CustomError("spi write and read err. ")

        r_data = list(r_data)[2:]
        #print(r_data)
        val = r_data[0]<<16 | r_data[1]<<8 | r_data[2]
        return val

    def _write_reg(self,reg,data,check=0):
        '''
        spi写数据
        :param reg: 寄存器地址
        :param data: 要写入的数据，三字节
        :param check: 写完是否检查有无写入
        :return: 0：成功 -1：失败
        '''
        h_byte = data >> 16
        m_byte = (data >> 8) & 0xff
        l_byte = (data >> 0) & 0xff

        check_sum = ~((0xA5 + reg + h_byte + m_byte + l_byte) & 0xFF)
        w_data = bytearray([0xA5,reg,h_byte,m_byte,l_byte,check_sum]) #0xA5:写识别字节
        if self._spi.write(w_data, len(w_data)) == -1:
            raise CustomError("spi write err. ")
        if check == 0:
            return 0
        r_data = self._read_reg(reg)
        if r_data == data:
            return 0
        return -1

    def reset(self):
        '''
        重置
        :return:
        '''
        #spi reset
        w_data = bytearray([0xff,0xff,0xff,0xff,0xff,0xff])
        self._spi.write(w_data,6)
        self._write_reg(SOFT_RESET,0x5a5a5a)

    @property
    def current_a(self):
        '''
        读a通道电流有效值
        :return: a通道电流有效值
        '''
        current_a = self._read_reg(IA_RMS)
        return current_a

    @property
    def current_b(self):
        '''
        读b通道电流有效值
        :return: b通道电流有效值
        '''
        current_b = self._read_reg(IB_RMS)
        return current_b

    @property
    def voltage(self):
        '''
        读电压有效值
        :return: 电压有效值
        '''
        vol = self._read_reg(V_RMS)
        return vol

    def read(self):
        '''
        :return: a,b,电压的三元组
        '''
        return (self.current_a,self.current_b,self.voltage)

if __name__ == '__main__':
    bl0939 = Bl0939(port=1)
    for i in range(10):
        ia,ib,vol = bl0939.read()
        print("a的电流有效值：{0}, b的电流有效值：{1}, 电压有效值：{2}".format(ia,ib,vol))
        utime.sleep(1)

