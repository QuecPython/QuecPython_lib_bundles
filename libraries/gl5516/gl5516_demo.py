'''
@Author: Stephen.Gao
@Date: 2022-03-22
@Description: gl5516 sensor demo

Copyright 2022 - 2023 quectel
'''
from misc import ADC
import utime as time
from usr.gl5516 import Gl5516


if __name__ == "__main__":
    AdcDevice = ADC()
    gl5516=Gl5516(AdcDevice,ADC.ADC0)
    for i in range(10):
        print("Photoresistor resistance as {0}Ω".format(gl5516.read()))
        time.sleep(1)

    print("measure end. ")