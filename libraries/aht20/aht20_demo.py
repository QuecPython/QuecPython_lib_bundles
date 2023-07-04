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
