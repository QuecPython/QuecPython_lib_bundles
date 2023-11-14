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
File: aht20.py
Project: i2c
File Created: Monday, 28th December 2020 5:17:28 pm
Author: chengzhu.zhou
-----
Last Modified: Tuesday, 15th March 2022 1:50:35 pm
Modified By: Stephen.Gao
-----
Copyright 2022 - 2022 quectel
'''

from machine import I2C
import utime as time
from usr.aht20 import Aht20


if __name__ == "__main__":
    aht_dev=Aht20()
    hum,tem=aht_dev.read()
    print("current humidity is {0}%,current temperature is {1}°C".format(hum,tem))
