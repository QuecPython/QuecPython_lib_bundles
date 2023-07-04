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