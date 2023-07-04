'''
@Author: Stephen.Gao
@Date: 2023-03-22
@Description: adxl346 sensor demo

Copyright 2022 - 2023 quectel
'''

import utime
from machine import I2C,Pin
from usr.adxl346 import Adxl346

# register address
REG_DEVID			= 0x00	# Device ID
REG_THRESH_TAP		= 0x1D	# Tap threshold 
REG_OFSX			= 0x1E	# X-axis offset 
REG_OFSY			= 0x1F	# Y-axis offset 
REG_OFSZ			= 0x20	# Z-axis offset 
REG_DUR				= 0x21	# Tap duration 
REG_Latent			= 0x22	# Tap latency 
REG_Window			= 0x23	# Tap window 
REG_THRESH_ACT		= 0x24	# Activity threshold 
REG_THRESH_INACT	= 0x25	# Inactivity threshold 
REG_TIME_INACT		= 0x26	# Inactivity time 
REG_ACT_INACT_CTL	= 0x27	# Axis enable control for activity and inactivity detection 
REG_THRESH_FF		= 0x28	# Free-fall threshold 
REG_TIME_FF			= 0x29	# Free-fall time 
REG_TAP_AXES		= 0x2A	# Axis control for single tap/double tap 
REG_ACT_TAP_STATUS	= 0x2B	# Source of single tap/double tap 
REG_BW_RATE			= 0x2C	# Data rate and power mode control 
REG_POWER_CTL		= 0x2D	# Power-saving features control 
REG_INT_ENABLE		= 0x2E	# Interrupt enable control 
REG_INT_MAP			= 0x2F	# Interrupt mapping control
REG_INT_SOURCE      = 0x30  # Interrupt source
REG_DATA_FORMAT		= 0x31	# Data format control 
REG_DATAX0			= 0x32	# X-Axis Data 0 
REG_DATAX1			= 0x33	# X-Axis Data 1 
REG_DATAY0			= 0x34	# Y-Axis Data 0 
REG_DATAY1			= 0x35	# Y-Axis Data 1 
REG_DATAZ0			= 0x36	# Z-Axis Data 0 
REG_DATAZ1			= 0x37	# Z-Axis Data 1
REG_TAP_SIGN		= 0x3A	# Sign and source for single tap/double tap 

# Bandwidth register configuration
BW_SEL_100 = 0x0A  # Bandwidth = 100Hz
BW_SEL_200 = 0x0B  # Bandwidth = 200Hz
BW_SEL_400 = 0x0C  # Bandwidth = 400Hz
BW_SEL_800 = 0x0D  # Bandwidth = 800Hz
BW_SEL_1600 = 0x0E  # Bandwidth = 1600Hz
BW_SEL_3200 = 0x0F  # Bandwidth = 3200Hz

# cmd of interrupt
SING_TAP_INT = 0X40 # single tap interrupt
DOUB_TAP_INT = 0X20 # double tap interrupt
ACT_INT = 0X10      # act interrupt
INACT_INT = 0X08    # inactiveness interrupt
FF_INT = 0X04       # free fall interrupt

range_2g = 0x00
range_4g = 0x01
range_8g = 0x02
range_16g = 0x03


if __name__ == "__main__":
    i2c_dev = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    adxl = Adxl346(i2c_dev)
    adxl.set_range(0x02) #8G range
    adxl.int_enable(DOUB_TAP_INT)
    for i in range(10):
        adxl.process_double_tap()
        x,y,z = adxl.read_acceleration()
        print("Acceleration in X-Axis : {} g" .format(x))
        print("Acceleration in Y-Axis : {} g" .format(y))
        print("Acceleration in Z-Axis : {} g" .format(z))
        print(" ************************************* ")

        utime.sleep(1)