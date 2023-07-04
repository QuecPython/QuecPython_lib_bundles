from machine import I2C
import utime as time
from usr.aht10 import Aht10


if __name__ == "__main__":
    aht_dev=Aht10()
    hum,tem=aht_dev.read()
    print("current humidity is {0}%,current temperature is {1}°C".format(hum,tem))
