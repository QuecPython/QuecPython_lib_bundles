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

from usr.st7789 import LCD_ST7789
from usr import CommonCamera
import utime as time

def cap_callback(LCD):
    LCD.Clear(0xFFFF)
    time.sleep(2)
    LCD._lcd.lcd_show_jpg('/usr/pic_01.jpeg', 0, 0)

if __name__ == '__main__':
    new_lcd = LCD_ST7789()
    print("lcd init. ")
    my_gc032a = CommonCamera(0,capt_callback=cap_callback)
    my_gc032a.cap_open()
    time.sleep(1)
    my_gc032a.start(name="pic_01")

