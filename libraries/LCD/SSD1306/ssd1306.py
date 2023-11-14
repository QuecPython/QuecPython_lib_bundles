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

import utime
from machine import LCD,Pin
import utime as time


class Ssd1306():
    def __init__(self, width, height, clk, InitData=None):
        self._lcd_w = width
        self._lcd_h = height
        self._lcd_clk = clk

        init_para = (
            2, 0, 120,

            # 0, 0, 0xae,     # 关显示
            # 0, 0, 0xd5,     # 设置显示时钟分频率、振荡器频率
            # 0, 0, 0xd5,     # 设置显示时钟分频率、振荡器频率
            # 0, 0, 0x80,
            # 0, 0, 0xa8,
            # 0, 0, 0x3f,
            # 0, 0, 0xd3,
            # 0, 0, 0x00,
            # 0, 0, 0x40,
            # 0, 0, 0x8d,
            # 0, 0, 0x10,
            # # 0, 0, 0x14,
            # 0, 0, 0x20,
            # 0, 0, 0x00,
            # 0, 0, 0xA1,
            # 0, 0, 0xc8,     # 行扫描顺序：从上到下c8	//上下颠倒c0
            # 0, 0, 0xa1,     # 列扫描顺序：从左到右a1	//左右翻转a0
            # 0, 0, 0xda,
            # 0, 0, 0x12,
            # 0, 0, 0x81,     # 微调对比度,本指令的0x81不要改动，改下面的值
            # 0, 0, 0x9f,
            # # 0, 0, 0xcf,     # 微调对比度的值，可设置范围0x00～0xff
            # 0, 0, 0xd9,
            # 0, 0, 0x22,
            # # 0, 0, 0xf1,
            # 0, 0, 0xa1,
            # 0, 0, 0xdb,
            # 0, 0, 0x40,
            # 0, 0, 0xa4,
            # 0, 0, 0xa6,
            0,0,0xae,
            0,1,0x20,
            1,1,0x00,
            0,0,0x40,
            0,0,0xa1,
            0,1,0xa8,
            1,1,0x3f,
            0,0,0xc8,
            0,1,0xd3,
            1,1,0x00,
            0,1,0xda,
            1,1,0x12,
            0,1,0xd5,
            1,1,0x80,
            0,1,0xd9,
            1,1,0xf1,
            0,1,0xdb,
            1,1,0x30,
            0,1,0xff,
            0,0,0xa4,
            0,0,0xa6,
            0,1,0x8d,
            1,1,0x14,
            0,0,0xaf,
            )

        invalid = (
            0, 0, 0x21,
            0, 0, 0x00,
            0, 0, 0x7F,
            0, 0, 0x22,
            0, 0, 0x00,
            0, 0, 0x07,
            )

        if InitData is None:
            self._initData = bytearray(init_para)
        else:
            self._initData = InitData

        self._invalidData = bytearray(invalid)

        self.lcd = LCD()
        self.lcd.lcd_init(self._initData,
                           self._lcd_w,
                           self._lcd_h,
                           self._lcd_clk,
                           1,
                           4,
                           1,
                           self._invalidData,
                           None,
                           None,
                           None)


if __name__ == '__main__':
    lcd = Ssd1306(128,64,6500)
    # # image_test = bytearray(image_data)
    lcd.lcd.lcd_clear(0xffff)
    utime.sleep(1)
    lcd.lcd.lcd_clear(0x0000)




