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
@Date: 2022-03-22
@Description: gl5516 sensor driver

Copyright 2022 - 2022 quectel
'''
from misc import ADC
import utime as time

# unit as Ω
class Gl5516(object):
    '''
    gl5516 class
    API：read()
    '''
    def __init__(self,adc_dev,adcn):
        self.adc = adc_dev
        self._adcn = adcn

    def _voltage_to_resistance(self,Volt):
        Va = 2 * Volt
        resistance = (2 * 4700 * 40200 * Va) / (2 * 4700 * (3300 - Va) - (40200 * Va))
        return resistance

    def read_volt(self):
        volt = self.adc.read(self._adcn)
        return volt

    def read(self):
        '''
        Read photoresistor value
        :return: photoresistor value
        '''
        volt = self.read_volt()
        resistance = self._voltage_to_resistance(volt)
        return resistance

if __name__ == "__main__":
    AdcDevice = ADC()
    gl5516=Gl5516(AdcDevice,ADC.ADC0)
    for i in range(10):
        print("Photoresistor resistance as {0}Ω".format(gl5516.read()))
        time.sleep(1)

    print("measure end. ")