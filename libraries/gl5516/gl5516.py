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