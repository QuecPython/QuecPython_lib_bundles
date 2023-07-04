from machine import I2C
import utime as time
from usr.htsensor import HtSensor


class Aht10(HtSensor):
    '''
    AHT10类
    '''

    # Initialization command
    AHT10_CALIBRATION_CMD = 0xE1
    # Trigger measurement
    AHT10_START_MEASURMENT_CMD = 0xAC
    # reset
    AHT10_RESET_CMD = 0xBA

    def __init__(self,addre=0x38):
        super().__init__(self)
        self._aht10_init(addre)

    def _aht10_init(self, addre):
        '''
        initialize the sensor
        '''
        self.i2c_dev = I2C(I2C.I2C1, I2C.FAST_MODE)
        self.i2c_addre = addre
        self.init_data = [0x08, 0x00]

        # print("sensor init begin.")

        super()._write_data([self.AHT10_CALIBRATION_CMD], self.init_data)
        time.sleep_ms(300)  # at last 300ms

        # print("sensor init complete.")

    def _aht10_transfor_data(self, data):
        '''
        Convert humidity and temperature according to the description in the datasheet
        '''
        r_data = data
        # humidity
        humidity = (r_data[0] << 12) | (
            r_data[1] << 4) | ((r_data[2] & 0xF0) >> 4)
        humidity = (humidity/(1 << 20)) * 100.0
        # print("current humidity is {0}%".format(humidity))
        # temperature
        temperature = ((r_data[2] & 0xf) << 16) | (
            r_data[3] << 8) | r_data[4]
        temperature = (temperature * 200.0 / (1 << 20)) - 50
        # print("current temperature is {0}°C".format(temperature))
        return (humidity,temperature)

    def read(self):
        data = super()._trigger_measure()
        return self._aht10_transfor_data(data)

    def aht10_test(self,count):
        for i in range(count):
            print("test %d begin." % (i+1))
            data = super()._trigger_measure()
            self._aht10_transfor_data(data)
            print("test %d end." % (i+1))
            super().ht_sensor_reset()
            time.sleep(1)
