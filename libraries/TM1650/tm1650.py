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
import _thread
import utime
#from usr.cutils import CPower
PINS = [getattr(Pin,"GPIO"+str(i)) for i in  range(1,18) ]

class Tm1650(object):
    '''
    Tm1650类
    开放接口：on(),off(),all_clear(),light(self, addr, data,is_point=False,is_auto=False)，
            clear_bit(bit),all_show(),show_num(num),show_str(st),show_dp(bit)
            circulate_show(st)
    '''
    CONTROL_CMD = 0x48
    SCANKEY_CMD = 0x49

    DISPLAY_ON =  0x11
    DISPLAY_OFF = 0x10
    a = 0x01
    b = 0x02
    c = 0x04
    d = 0x08
    e = 0x10
    f = 0x20
    g = 0x40
    dp = 0x80
    DATA_ADDR1 = 0x68
    DATA_ADDR2 = 0x6A
    DATA_ADDR3 = 0x6C
    DATA_ADDR4 = 0x6E
    DIO_PIN = Pin.GPIO10
    CLK_PIN = Pin.GPIO13

    LIGHT_MAPPING = {
        1: DATA_ADDR1,
        2: DATA_ADDR2,
        3: DATA_ADDR3,
        4: DATA_ADDR4,
        5: CONTROL_CMD
    }
    # "-": 0x40,
    DISPLAY_MAPPING = {"0": a | b | c | d| e | f, "1": b | c, "2": a | b | g | e | d, "3": a | b | g | c | d,
                       "4": f  |g | b | c, "5": a | f | g | c | d, "6": a | f | g | c | d | e, "7": a | b | c,
                       "8": a | b | c | d | e | f | g, "9": a | b | c | d | f | g,
                       "A": a | b | c | e | f | g, "b": c | d | e | f | g, "C":a|f|e|d,"c": g|e|d,"d": b | c | d | e | g,
                       "E": a | d | e | f | g, "F": a | e | f | g, "on": DISPLAY_ON, "p": a | b | g | f | e,"P":a | b | g | f | e,
                       "S": a | f | g | c|d, "r": g | e, "t": f | g | e | d, "i": b|c,"s": a|f | g | c|d,
                       "L": f | e | d, "H": f | e | g | b | c, "n": e | g | c,"h":f | e | g  | c,"I":f|e,"J": b|c|d|e,"O": c | d | e | g,
                       "off": DISPLAY_OFF,"cl": 0x00, " ":0x00,"4g": a, "cool": f, "alarm": e, "wifi": d, "def": dp,".":dp,
                       "-": g, 0x00: 0x00, "_": b|g|e}

    def __init__(self, dio=None, clk=None):
        if dio == clk:
            dio = clk = None
        if dio and dio  in PINS:
            self._dio_PIN = dio
        if clk and clk  in PINS:
            self._clk_PIN = clk
        self._dio = Pin(self._dio_PIN, Pin.OUT, Pin.PULL_DISABLE, 1)  # Tm1650 DIO
        self._clk = Pin(self._clk_PIN, Pin.OUT, Pin.PULL_DISABLE, 1)  # Tm1650 CLK
        self._light_lock = _thread.allocate_lock()

    # def _delay_us(self, num=3000):
    def _delay_us(self, num=300):
        # utime.sleep_ms(1)
        while num > 0:
            num  = num -1

    def _start_signal(self):
        self._clk.write(1)
        self._delay_us(200)
        self._dio.write(1)
        self._delay_us(200)
        self._dio.write(0)
        self._delay_us(200)
        self._clk.write(0)

    def _stop_signal(self):
        self._dio.write(0)
        self._delay_us(200)
        self._clk.write(1)
        self._delay_us(200)
        self._dio.write(1)
        self._delay_us(200)
        self._clk.write(0)
        self._delay_us(200)
        self._dio.write(0)

    def _wait_ack(self):
        # self._dio.write(1)
        self._dio = Pin(self._dio_PIN, Pin.IN, Pin.PULL_PU, 0)
        # self._delay_us()
        self._clk.write(1)
        self._delay_us()
        i = 0
        while (self._dio.read()):
            i += 1
            print("i = ",i)
            if i > 700:
                self._dio = Pin(self._dio_PIN, Pin.OUT, Pin.PULL_DISABLE, 1)  # Tm1650 DIO
                self._clk.write(0)
                self._delay_us()
                self._stop_signal()
                raise Exception("数据通信错误")
        self._clk.write(0)
        self._delay_us()
        self._dio = Pin(self._dio_PIN, Pin.OUT, Pin.PULL_DISABLE, 1)  # Tm1650 DIO

    def _write_data(self, data):
        self._clk.write(0)
        self._delay_us(200)
        for j in range(8):
            if data & 0x80:
                self._dio.write(1)
            else:
                self._dio.write(0)
            self._delay_us()
            self._clk.write(1)
            self._delay_us()
            self._clk.write(0)
            data <<= 1

    def light(self, addr, data,is_point=False,is_auto=False):
        '''
        写数据命令或往显存地址写显示数据
        :param addr: 寄存器地址
        :param data: 写入的数据
        :param is_point: 是否是点
        :param is_auto: 是否需要字符转化
        '''
        try:
            self._light_lock.acquire()
            if is_auto:
                if data not in self.DISPLAY_MAPPING:
                    data = "0"
                data = self.DISPLAY_MAPPING[data]

            if is_point:
                data = data | self.DISPLAY_MAPPING["."]
            self._start_signal()
            self._write_data(self.LIGHT_MAPPING[addr])
            self._wait_ack()
            self._write_data(data)
            self._wait_ack()
            self._stop_signal()
        except Exception as e:
            print(e,addr,data,_thread.get_ident())
            # if addr ==2 or addr==3:
            #CPower.restart()
        finally:
            self._light_lock.release()

    def on(self):
        times = 3
        while times > 0 and self.light(5, "on", is_auto=True):
            # self.light(5, "on", is_auto=True)
            utime.sleep(1)
            times = times - 1

    def off(self):
        self.light(5, "off", is_auto=True)

    def all_clear(self):
        '''
        清除全部显示
        '''
        try:
            for i in range(1,5):
                self.light(i, "cl", is_auto=True)
        except Exception as e:
            print(e)

    def clear_bit(self,bit):
        '''
        清除一位显示
        '''
        if bit > 4 or bit < 1:
            return -1
        try:
            self.light(bit, "cl", is_auto=True)
        except Exception as e:
            print(e)

    def all_show(self):
        '''
        全显
        '''
        try:
            self.light(1, 0xff)
            self.light(2, 0xff)
            self.light(3, 0xff)
            self.light(4, 0xff)
        except Exception as e:
            print(e)

    def show_num(self, num):
        '''
        显示数字，不满四位的靠右显示
        :param num: 数字 -999 ~ 9999
        :return: -1:error 0:success
        '''
        if num < -999 or num > 9999:
            return -1
        try:
            if num < 0:
                self.light(1,'-',is_auto=True)
                num = -num
            else:
                self.light(1,str((num // 1000) % 10),is_auto=True)
            self.light(2, str((num // 100) % 10),is_auto=True)
            self.light(3, str((num // 10) % 10),is_auto=True)
            self.light(4, str(num % 10),is_auto=True)
            return 0
        except Exception as e:
            print(e)

    def show_str(self,st):
        '''
        显示字符串,不足四位的靠右显示
        :param st: 字符串
        :return: -1:error 0:success
        '''
        if len(st) > 4:
            return -1
        bits = len(st)
        try:
            for ch in st[::1]:
                if ch not in self.DISPLAY_MAPPING:
                    return -1
                else:
                    self.light(5 - bits,ch,is_auto=True)
                    bits -= 1
            return 0
        except Exception as e:
            print(e)

    def show_dp(self, bit=1):
        '''
        显示点
        :param bit: 显示在第几位，范围1-4，默认1
        :return: -1:error 0:success
        '''
        if bit > 4 or bit < 1:
            return -1
        self.light(bit,'.',is_auto=True)
        return 0

    def circulate_show(self,st):
        '''
        循环显示字符串或数字
        :param st: 字符串12字节以内
        :return: -1:字符串过长
        '''
        show_lst = []
        circle = 0
        if len(st) > 4:
            new_str = st + st
            for i in range(len(st)):
                show_lst.append(new_str[i:i+4])
        else:
            null_count = 4 - len(st)
            new_str = ' ' * null_count + st
            new_str += new_str
            for i in range(4):
                show_lst.append(new_str[i:i+4])
        while 1:
            self.show_str(show_lst[circle])
            if circle == len(show_lst) - 1:
                circle = 0
            else:
                circle += 1
            utime.sleep(0.5)

if __name__ == "__main__":
    tube = Tm1650(Pin.GPIO13, Pin.GPIO12) #600U PIN60,PIN59
    tube.on()
    tube.all_show()
    utime.sleep(1)
    tube.clear_bit(3)
    utime.sleep(1)
    tube.all_clear()
    utime.sleep(1)
    tube.show_dp(3)
    utime.sleep(1)
    tube.show_str("PPJ")
    utime.sleep(1)
    tube.show_num(-537)
    utime.sleep(1)
    tube.show_num(8537)
    utime.sleep(1)
    tube.circulate_show("AbCdEFH")
