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
@Description: gl5528 sensor driver

Copyright 2022 - 2022 quectel
'''
from misc import ADC
import utime as time

o2i_table = {40000:1,26350:2,20640:3,17360:4,15170:5,13590:6,12390:7,
             11430:8,10650:9,9990:10,9440:11,8950:12,8530:13,8160:14,
             7830:15,7530:16,7260:17,7010:18,6790:19,6580:20,6390:21,
             6210:22,6050:23,5900:24,5750:25,5620:26,5490:27,5370:28,
             5260:29,5160:30,5050:31,4960:32,4870:33,4780:34,4700:35,
             4620:36,4540:37,4470:38,4400:39,4330:40,4270:41,4210:42,
             4150:43,4090:44,4040:45,3980:46,3930:47,3880:48,3840:49,
             3790:50,3740:51,3700:52,3660:53,3620:54,3580:55,3540:56,
             3500:57,3460:58,3430:59,3390:60,3360:61,3330:62,3300:63,
             3270:64,3230:65,3210:66,3180:67,3150:68,3120:69,3090:70,
             3070:71,3040:72,3020:73,2990:74,2970:75,2940:76,2920:77,
             2900:78,2880:79,2850:80,2830:81,2810:82,2790:83,2770:84,
             2750:85,2730:86,2710:87,2690:88,2680:89,2660:90,2640:91,
             2620:92,2610:93,2590:94,2570:95,2560:96,2540:97,2530:98,
             2510:99,2490:100,2480:101,2460:102,2450:103,2440:104,
             2420:105,2410:106,2390:107,2380:108,2370:109,2360:110,
             2340:111,2330:112,2320:113,2300:114,2290:115,2280:116,
             2270:117,2260:118,2250:119,2230:120,2220:121,2210:122,
             2200:123,2190:124,2180:125,2170:126,2160:127,2150:128,
             2140:129,2130:130,2120:131,2110:132,2100:133,2090:134,
             2080:135,2070:136,2060:137,2050:138,2040:139,2030:141,
             2020:142,2010:143,2000:144,1990:145,1980:147,1970:148,
             1960:149,1950:150,1940:152,1930:153,1920:154,1910:155,
             1900:157,1890:158,1880:160,1870:161,1860:162,1850:164,
             1840:165,1830:167,1820:168,1810:170,1800:171,1790:173,
             1780:175,1770:176,1760:178,1750:180,1740:181,1730:183,
             1720:185,1710:187,1700:188,1690:190,1680:192,1670:194,
             1660:196,1650:198,1640:200,1630:202,1620:204,1610:206,
             1600:208,1590:210,1580:212,1570:215,1560:217,1550:219,
             1540:222,1530:224,1520:226,1510:229,1500:231,1490:234,
             1480:237,1470:239,1460:242,1450:245,1440:248,1430:250,
             1420:253,1410:256,1400:259,1390:262,1380:266,1370:269,
             1360:272,1350:275,1340:279,1330:282,1320:286,1310:289,
             1300:293,1290:297,1280:300,1270:304,1260:308,1250:312,
             1240:317,1230:321,1220:325,1210:330,1200:334,1190:339,
             1180:344,1170:348,1160:353,1150:358,1140:364,1130:369,
             1120:374,1110:380,1100:386,1090:391,1080:397,1070:403,
             1060:410,1050:416,1040:423,1030:430,1020:436,1010:444,
             1000:451,990:458,980:466,970:474,960:482,950:491,940:499,
             930:508,920:517,910:526,900:536,890:546,880:556,870:567,
             860:578,850:589,840:600,830:612,820:625,810:637,800:650,
             790:664,780:678,770:692,760:707,750:723,740:739,730:756,
             720:773,710:791,700:809,690:829,680:849,670:869,660:891,
             650:914,640:937,630:961,620:987}

# unit as Ω
class Gl5528(object):
    '''
    gl5528 class
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

    def r2i(self,resis):
        res_to_find = int(int(resis) // 10 * 10)
        lux = o2i_table.get(res_to_find)
        if lux:
            return lux
        else:
            return None

    def read(self):
        '''
        Read the Photoresistor value and illuminance (unit: lux, error, if found in the corresponding table)
        :return: (photoresistor value(Ω),illuminance(lux))
        '''
        volt = self.read_volt()
        resistance = self._voltage_to_resistance(volt)
        res_to_find = int(int(resistance) // 10 * 10)
        lux = o2i_table.get(res_to_find)
        return (resistance,lux)

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