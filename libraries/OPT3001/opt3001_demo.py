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