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

from machine import Pin
import utime as time

ACK = 0
NACK = 1

rdaclk = Pin.GPIO2
rdadio = Pin.GPIO3

RDA_WRITE = 0x22
RDA_READ = 0x23

RDA_R00 = 0x00
RDA_R02 = 0x02
RDA_R03 = 0x03
RDA_R04 = 0x04
RDA_R05 = 0x05
RDA_R0A = 0x0A
RDA_R0B = 0x0B

class RDA5807(object):
    '''
    收音机RDA5807类
    开放接口：_rda_init(),fm_enable(),next_chanl(),seek_channel(),freq_set(freq),seekth_set(reei)
            rssi_get(),seek_direction(dir),vol_set(vol),mute_set(),bass_set(bass)
    '''
    def __init__(self,rdaclk,rdadio):
        self.CLK = Pin(rdaclk, Pin.OUT, Pin.PULL_DISABLE, 1) # PL5NF001 CLK
        self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1) # PL5NF001 DIO
        self._rda_init()

    def _delay_ms(self, ms):
        time.sleep_ms(ms)

    def _delay_us(self, num):
        pass

    def _start_signal(self):
        self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.DIO.write(1)
        self.CLK.write(1)
        self._delay_us(5)
        self.DIO.write(0)
        self._delay_us(5)
        self.CLK.write(0)
        self._delay_us(5)

    def _stop_signal(self):
        self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.CLK.write(0)
        self._delay_us(2)
        self.DIO.write(0)
        self._delay_us(2)
        self.CLK.write(1)
        self._delay_us(2)
        self.DIO.write(1)
        self._delay_us(2)

    def _ack(self, is_ack):
        self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.DIO.write(is_ack)
        self._delay_us(2)
        self.CLK.write(1)
        self._delay_us(4)
        self.CLK.write(0)

    def _wait_ack(self):
        i = 0
        self.CLK.write(0)
        self._delay_us(2)
        self.DIO = Pin(rdadio, Pin.IN, Pin.PULL_DISABLE, 1)
        self._delay_us(2)

        while (self.DIO.read()):
            i += 1
            if i > 2000:
                #self._stop_signal()
                print('iic stop')
                self.CLK.write(0)
                self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1)
                return 1
        self._delay_us(2)
        self.CLK.write(1)
        self._delay_us(2)
        self.CLK.write(0)
        #self._delay_us(2)
        return 0

    def _write_data(self, data):
        self.DIO = Pin(rdadio, Pin.OUT, Pin.PULL_DISABLE, 1)
        j = 0
        for j in range(0,8):
            self.CLK.write(0)
            self._delay_us(2)
            if data & 0x80:
                self.DIO.write(1)
            else:
                self.DIO.write(0)
            data <<= 1
            self._delay_us(2)
            self.CLK.write(1)
            self._delay_us(2)

        self.CLK.write(0)

        self._wait_ack()

    def _read_byte(self, ack):
        self.DIO = Pin(rdadio, Pin.IN, Pin.PULL_DISABLE, 1)
        recive = 0
        time.sleep_ms(12)
        for i in range(0, 8):
            recive <<= 1
            self.CLK.write(0)
            self._delay_us(2)
            self.CLK.write(1)
            self._delay_us(2)
            level = self.DIO.read()
            if level == 1:
                recive |= 1
        self.CLK.write(0)
        self._ack(ack)
        return recive


    def _ReadReg(self, regaddr):
        self._start_signal()
        self._write_data(RDA_WRITE)
        self._write_data(regaddr)
        self._start_signal()
        self._write_data(RDA_READ)
        buf = self._read_byte(ACK)
        buf <<= 8
        buf = buf | self._read_byte(NACK)
        self._stop_signal()
        print("read reg =",buf)
        return buf

    def _WriteReg(self, reg, val):
        self._start_signal()
        self._write_data(RDA_WRITE)
        self._write_data(reg)
        self._write_data(val >> 8)
        self._write_data(val & 0xFF)
        self._stop_signal()

    def vol_set(self, vol):
        '''
        音量设置
        :param vol: 0-15
        '''
        temp = self._ReadReg(RDA_R05)
        print("vol set:",temp)
        temp &= 0xfff0  #0-3bit 音量
        self._WriteReg(RDA_R05,vol|temp)

    def mute_set(self, mute):
        '''
        静音设置
        :param mute: 1 静音 0 不静音
        '''
        tmp = self._ReadReg(RDA_R02)
        if(mute == 0):
            tmp |= (1<<14) #14bit置1，不静音
        else:
            tmp &= ~(1<<14)
        print("mute set:", tmp)
        self._WriteReg(RDA_R02, tmp)

    def bass_set(self, bass):
        '''
        声音低频
        :param bass:
        '''
        tmp = self._ReadReg(RDA_R02)
        if(bass):
            tmp |= (1<<12)
        else:
            tmp &= ~(1<<12)
        print("bass set:", tmp)
        self._WriteReg(RDA_R02, tmp)

    def rssi_get(self):
        '''
        信号强度获取 15-9bit
        :return 信号强度
        '''
        tmp = self._ReadReg(RDA_R0B)
        tmp = (tmp >> 9) & 0x7f
        return tmp

    def seekth_set(self,rssi):
        '''
        自动搜台信号阈值强度 14-8bit
        :param rssi:  0-15 默认为8 数值越低搜到的台越多
        '''
        rssi = rssi & 0xf
        tmp = self._ReadReg(RDA_R05)
        tmp &= ~(0xf<<8)
        tmp |= (rssi<<8)
        self._WriteReg(RDA_R05, tmp)

    def seek_direction(self,dir):
        '''
        搜台方向
        :param dir: 1：向上搜索 0：向下搜索
        '''
        tmp = self._ReadReg(RDA_R02)
        tmp &= ~(1<<9)
        if(dir == 1):
            tmp |= (1<<9)
        else:
            tmp |= (0<<9)
        #较旧版本修改点 写入寄存器RDA_R02
        self._WriteReg(RDA_R02, tmp)

    def freq_set(self, freq):
        '''
        频率设置 单位是10Khz
        :param freq: 6500~10800
        '''
        tmp = self._ReadReg(RDA_R03)
        tmp &= 0x001F
        band = (tmp>>2)&0x03
        spc = tmp & 0x03

        if(spc == 0):
            spc = 10
        elif(spc == 1):
            spc = 20
        else:
            spc = 5

        if(band == 0):
            fbtm = 8700
        elif(band == 1 or (band == 2)):
            fbtm = 7600
        else:
            fbtm = self._ReadReg(0x53)
            fbtm *= 10

        if(freq < fbtm):
            print("freq < fbtm")
            return

        chan = int((freq - fbtm)/spc)
        chan &= 0x3ff
        tmp |= (chan<<6)
        tmp |= (1<<4)
        self._WriteReg(RDA_R03, tmp)
        time.sleep_ms(20)

    def seek_channel(self):
        '''
        自动搜台
        '''
        tmp = self._ReadReg(RDA_R02)
        tmp |= (1<<8)
        self._WriteReg(RDA_R02, tmp)
        while((self._ReadReg(RDA_R0A) & (1<<14)) == 0):
            time.sleep_ms(10)

        tmp = (self._ReadReg(RDA_R0A) & 0x3ff) *100000 + 87000000
        print("seek channel:",tmp)
        return tmp/10000

    def fm_enable(self,flag):
        '''
        使能芯片
        :param flag: 1.使能 0：禁用
        '''
        tmp = self._ReadReg(RDA_R02)
        if(flag == 1):
            tmp |= 1
        
        if(flag == 0):
            tmp &= ~(0x1)

        self._WriteReg(RDA_R02,tmp)

    def _rda_init(self):
        '''
        RDA 初始化
        '''
        self._WriteReg(RDA_R02, 0x0002)
        time.sleep_ms(30)
        self._WriteReg(RDA_R02, 0xd281)
        self._WriteReg(RDA_R03, 0x0000)
        self._WriteReg(RDA_R04, 0x0040)
        self._WriteReg(RDA_R05, 0x8880)

        self.fm_enable(1)

    def next_chanl(self):
        '''
        播放下个电台
        '''
        freq = self.seek_channel()

        if((self._ReadReg(RDA_R0B)>>8) & 0x01):
            print("is chan", freq)

        if((self._ReadReg(RDA_R0A)&0x01)):
            print("SF = 1")
            self.freq_set(freq)



if __name__ == '__main__':
    test_pm = RDA5807(rdaclk = Pin.GPIO2,rdadio = Pin.GPIO3)
    test_pm._rda_init()
    print("init finish. ")
    test_pm.seek_channel()
    print("channel seeking...")
    test_pm.vol_set(15)
    print('vol seted to 15.')
    test_pm.fm_enable(0)
    print("radio forbid.")
    

