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
@Date: 2022-03-23
@Description: gl5528 sensor demo

Copyright 2022 - 2023 quectel
'''
from misc import ADC
import utime as time
from usr.gl5528 import Gl5528


if __name__ == "__main__":
    AdcDevice = ADC()
    gl5528=Gl5528(AdcDevice,ADC.ADC0)
    for i in range(10):
        resis,lux=gl5528.read()
        if lux:
            print("Photoresistor resistance as {0}Ω,lux is {1}".format(resis,lux))
        else:
            print("Photoresistor resistance as {0}Ω".format(resis))
        time.sleep(1)

    print("measure end. ")