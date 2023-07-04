'''
@Author: Stephen.Gao
@Date: 2022-04-06
@Description: HDC1080 sensor demo

Copyright 2022 - 2022 quectel
'''
from machine import I2C
import utime as time
from usr.hdc1080 import Hdc1080


if __name__ == "__main__":
    i2c_dev = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    hdc=Hdc1080(i2c_dev)
    for i in range(10):
        print("test %d begin." % (i + 1))
        hum, tem = hdc.read()
        print("current humidity is {0}%RH,current temperature is {1}°C".format(hum, tem))
        print("test %d end." % (i + 1))
        time.sleep(1)
