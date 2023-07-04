'''
@Author: Stephen.Gao
@Date: 2023-03-22
@Description: adxl346 sensor driver

Copyright 2022 - 2023 quectel
'''

import utime
from machine import I2C,Pin

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


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo=ErrorInfo

    def __str__(self):
        return self.errorinfo


class Adxl346(object):
    def __init__(self,i2c,dev_addr=0x53):
        self._i2c = i2c
        self._dev_addr = dev_addr

        if self._read_data(REG_DEVID,1)[0] != 0xE6:
            raise CustomError("device id err.")
        self._write_data(REG_DATA_FORMAT, 0x08)     # High level interrupt output, 13 bit resolution, right aligned output data, 2g range
        self._write_data(REG_BW_RATE,BW_SEL_100)    # 100Hz
        self._write_data(REG_POWER_CTL,0x08)        # Measurement mode
        self._write_data(REG_INT_ENABLE,0x00)       # Interrupt not enabled
        self._write_data(REG_OFSX, 0x00)
        self._write_data(REG_OFSY, 0x00)
        self._write_data(REG_OFSZ, 0x00)

    def _read_data(self, regaddr, datalen):
        '''
        i2c read data
        :param regaddr: register address
        :param datalen: read data length
        :return: data
        '''
        r_data = bytearray(datalen)
        reg_addres = bytearray([regaddr])
        self._i2c.read(self._dev_addr, reg_addres, 1, r_data, datalen, 1)
        ret_data = list(r_data)
        return ret_data

    def _write_data(self, regaddr, data):
        '''
        i2c write data
        :param regaddr: register address
        :param datalen: data to write
        '''
        addr = bytearray([regaddr])
        w_data = bytearray([data])
        self._i2c.write(self._dev_addr, addr, len(addr), w_data, len(w_data))

    def set_range(self,range=range_2g):
        '''
        Configure sensor range,REG_DATA_FORMAT 0-1bit
        :param range: acceleration range, default 2g
        '''
        value = self._read_data(REG_DATA_FORMAT, 1)[0]
        value &= 0xF0
        value |= range
        value |= 0x08
        self._write_data(REG_DATA_FORMAT, value)

    @property
    def _resolution(self):
        """
        Obtain the range of the accelerometer.
        :return: range_2_G, range_4_G, range_8_G,, range_16_G.
        """
        range = self._read_data(REG_DATA_FORMAT, 1)[0]
        range &= 0x03
        return range

    def read_acceleration(self):
        """
        read acceleration
        @return x y and z axis acceleration values, in g
        """
        data = self._read_data(REG_DATAX0,6)
        accel_range = self._resolution

        mult = 0.004

        x = data[0] | (data[1] << 8)
        if (x & (1 << 16 - 1)):
            x = x - (1 << 16)

        y = data[2] | (data[3] << 8)
        if (y & (1 << 16 - 1)):
            y = y - (1 << 16)

        z = data[4] | (data[5] << 8)
        if (z & (1 << 16 - 1)):
            z = z - (1 << 16)

        x = x * mult
        y = y * mult
        z = z * mult

        if accel_range == 3:        #range_16_G
            # print("16G range")
            x = x if x <= 16 else x - 32
            y = y if y <= 16 else y - 32
            z = z if z <= 16 else z - 32
        elif accel_range == 2:      #range_8_G
            # print("8G range")
            x = x if x <= 8 else x - 16
            y = y if y <= 8 else y - 16
            z = z if z <= 8 else z - 16
        elif accel_range == 1:      #range_4_G
            # print("4G range")
            x = x if x <= 4 else x - 8
            y = y if y <= 4 else y - 8
            z = z if z <= 4 else z - 8
        elif accel_range == 0:      #range_2_G
            # print("2G range")
            x = x if x <= 2 else x - 4
            y = y if y <= 2 else y - 4
            z = z if z <= 2 else z - 4

        return (round(x,4), round(y,4), round(z,4))

    def clear_int(self,int_code):
        '''
        Clear an interrupt enable
        @param int_code: value to write into the interrupt enable register
        '''
        r_data = self._read_data(REG_INT_ENABLE, 1)[0]
        w_data = r_data & ~int_code
        self._write_data(REG_INT_ENABLE,w_data)

    def int_enable(self,int_code,tap_thr=0x30, dur=0x20,tap_axis=0x07 ,laten=0x15,window=0xff,ff_thr=0x06,
                   ff_time=0x15,act_thr=0x03,act_axis=0xf0,inact_thr=0x03,inact_axis=0x0f,inact_time=3):
        '''
        interrupt enable
        @param int_code: value to write into the interrupt enable register
        @return:  -1:fail  0:success
        '''
        self.clear_int(int_code)    # Clear this bit before enabling, follow the datasheet
        r_data = self._read_data(REG_INT_ENABLE, 1)[0]
        w_data = r_data | int_code
        if int_code == SING_TAP_INT:
            self._write_data(REG_THRESH_TAP, tap_thr)  # default 0x30
            self._write_data(REG_DUR,dur)          # default 0x20，>0x10
            self._write_data(REG_TAP_AXES, tap_axis)  # default 0x07
            # print('single_tap set suceess! ')
        elif int_code == DOUB_TAP_INT:
            self._write_data(REG_THRESH_TAP, tap_thr)  # default 0x30
            self._write_data(REG_DUR, dur)         # default 0x20，>0x10
            self._write_data(REG_TAP_AXES, tap_axis)  # default 0x07
            self._write_data(REG_Latent,laten)       # default 0x15
            self._write_data(REG_Window,window)       # default 0xff
            # print('double_tap set suceess! ')
        elif int_code == FF_INT:
            self._write_data(REG_THRESH_FF, ff_thr)  # default 0x06
            self._write_data(REG_TIME_FF, ff_time)    # default 0x15, 0x14 to 0x46
            # print('ff set suceess! ')
        elif int_code ==ACT_INT:
            self._write_data(REG_THRESH_ACT, act_thr)  # default 0x03
            self._write_data(REG_ACT_INACT_CTL, act_axis)  # Default setting for xyz three-axis AC coupling
            # print('act_int set suceess! ')
        elif int_code == INACT_INT:
            self._write_data(REG_THRESH_INACT, inact_thr)  # default 0x03
            self._write_data(REG_ACT_INACT_CTL, inact_axis)  # Default setting for xyz three-axis AC coupling
            self._write_data(REG_TIME_INACT, inact_time)  # default 0x03
            # print('inact_int set suceess! ')
        else:
            # print('int enable failed.check int_code.')
            return -1
        if self._write_data(REG_INT_ENABLE,w_data):
            raise CustomError("int enable failed.")
        return 0

    def process_single_tap(self):
        while 1:
            r_data = self._read_data(REG_INT_SOURCE,1)[0]
            if r_data & SING_TAP_INT:
                return 1
            utime.sleep_ms(20)

    def process_double_tap(self):
        while 1:
            r_data = self._read_data(REG_INT_SOURCE,1)[0]
            if r_data & DOUB_TAP_INT:
                return 1
            utime.sleep_ms(20)

    def process_act(self):
        while 1:
            r_data = self._read_data(REG_INT_SOURCE,1)[0]
            if r_data & ACT_INT:
                return 1
            utime.sleep_ms(20)

    def process_inact(self):
        while 1:
            r_data = self._read_data(REG_INT_SOURCE,1)[0]
            # print(r_data)
            if r_data & INACT_INT:
                return 1
            utime.sleep_ms(20)

    def process_ff(self):
        while 1:
            r_data = self._read_data(REG_INT_SOURCE,1)[0]
            if r_data & FF_INT:
                return 1
            utime.sleep_ms(20)


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