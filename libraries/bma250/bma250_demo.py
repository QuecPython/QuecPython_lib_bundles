'''
@Author: Stephen.Gao
@Date: 2023-03-22
@Description: bma250 sensor demo

Copyright 2022 - 2023 quectel
'''
import utime
from machine import I2C
from usr.bma250 import Bma250

# I2C address of the device
DEFAULT_ADDRESS = 0x19

DEVICE_ID = 0xf9

# BMA250 Register Map
CHIP_ID_REG = 0x00  # Chip ID Register

X_AXIS_LSB_REG = 0x02  # X-Axis Data LSB
X_AXIS_MSB_REG = 0x03  # X-Axis Data MSB
Y_AXIS_LSB_REG = 0x04  # Y-Axis Data LSB
Y_AXIS_MSB_REG = 0x05  # Y-Axis Data MSB
Z_AXIS_LSB_REG = 0x06  # Z-Axis Data LSB
Z_AXIS_MSB_REG = 0x07  # Z-Axis Data MSB

TEMP_RD_REG = 0x08  # Temperature Data

STATUS1_REG = 0x09  # Interrupt Status Register
STATUS2_REG = 0x0A  # New Data Status Register
STATUS_TAP_SLOPE_REG = 0x0B  # Tap and Hold Interrupt Status Register
STATUS_ORIENT_HIGH_REG = 0x0C  # Flat and Orientation Status Register
RANGE_SEL_REG = 0x0F  #
BW_SEL_REG = 0x10  #
MODE_CTRL_REG = 0x11  # Mode Control Register
DATA_CTRL_REG = 0x13  # Data Control Register
RESET_REG = 0x14  # Reset Register
INT_EN1_REG = 0x16  # 1
INT_EN2_REG = 0x17  # 2
LATCH_INT_REG = 0x21  #
HIGH_LOW_MODE_REG = 0x24    #
SLOPE_TH_REG = 0x28  #
RESET_CMD = 0xB6  # Reset Register

# BMA250 Range selection register configuration
RANGE_SEL_2G = 0x03  # Range = +/-2G
RANGE_SEL_4G = 0x05  # Range = +/-4G
RANGE_SEL_8G = 0x08  # Range = +/-8G
RANGE_SEL_16G = 0x0C  # Range = +/-16G

# BMA250 bandwidth register configuration
BW_SEL_7_81 = 0x08  # Bandwidth = 7.81Hz
BW_SEL_15_63 = 0x09  # Bandwidth = 15.63Hz
BW_SEL_31_25 = 0x0A  # Bandwidth = 31.25Hz
BW_SEL_62_5 = 0x0B  # Bandwidth = 62.5Hz
BW_SEL_125 = 0x0C  # Bandwidth = 125Hz
BW_SEL_250 = 0x0D  # Bandwidth = 250Hz
BW_SEL_500 = 0x0E  # Bandwidth = 500Hz
BW_SEL_1000 = 0x0F  # Bandwidth = 1000Hz

# Interrupt Enable Configuration
# int1 configure
slope_en_x = 0x01
slope_en_y = 0x02
slope_en_z = 0x04
slope_en_xyx = 0x07
d_tap_en = 0x10
s_tap_en = 0x20
orient_en = 0x40
flat_en = 0x80
# int2 configure
low_g_en = 0x04     #Low gravity, can be used for ff interrupt
high_g_en_x = 0x01
high_g_en_y = 0x02
high_g_en_z = 0x04
high_g_en_xyx = 0x07


if __name__ == "__main__":
    i2c_dev = I2C(I2C.I2C1,I2C.STANDARD_MODE)
    bma250 = Bma250(i2c_dev)
    bma250.set_range(RANGE_SEL_2G)
    bma250.set_hz(BW_SEL_1000)
    bma250.int_enable(orient_en)
    for i in range(10):
        utime.sleep(1)
        bma250.process_orient()
        x, y, z = bma250.read_acceleration()
        print("Acceleration in X-Axis : {} g".format(x))
        print("Acceleration in Y-Axis : {} g".format(y))
        print("Acceleration in Z-Axis : {} g".format(z))
        print(" ************************************* ")


