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
@Date: 2022-03-31
@Description: OPT3001 sensor demo

Copyright 2022 - 2023 quectel
'''

from machine import I2C
import utime
from usr.opt3001 import Opt3001


if __name__ == "__main__":
    i2c_obj=I2C(I2C.I2C1,I2C.FAST_MODE)
    opt = Opt3001(i2c_obj)
    for i in range(20):
        opt.set_measure_mode(1)
        utime.sleep_ms(1000)  # at least 800ms
        print("measurement times:{}------------".format(i+1))
        lux = opt.read()
        print("The light intensity is {0} lux".format(lux))