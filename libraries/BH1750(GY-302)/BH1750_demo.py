'''
@Author: Stephen.Gao
@Date: 2022-03-31
@Description: BH1750（GY302） sensor demo

Copyright 2022 - 2022 quectel
'''
import utime
from machine import I2C
from user.BH1750 import Bh1750


if __name__ == "__main__":
    i2c_obj=I2C(I2C.I2C1,I2C.STANDARD_MODE)
    bh1750 = Bh1750(i2c_obj)
    bh1750.on()
    bh1750.set_measure_mode()
    for i in range(10):
        print("the {} times------------".format(i+1))
        lux = bh1750.read()
        print("The light intensity is {0} lux".format(lux))
        utime.sleep_ms(1000)