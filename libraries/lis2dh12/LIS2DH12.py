'''
@Author: Stephen.Gao
@Date: 2023-03-22
@Description: LIS2DH12 sensor driver

Copyright 2022 - 2023 quectel
'''

import utime
from machine import I2C
from machine import ExtInt

LIS2DH12_OUT_X_L = 0x28
LIS2DH12_OUT_X_H = 0x29
LIS2DH12_OUT_Y_L = 0x2A
LIS2DH12_OUT_Y_H = 0x2B
LIS2DH12_OUT_Z_L = 0x2C
LIS2DH12_OUT_Z_H = 0x2D
LIS2DH12_FIFO_CTRL_REG = 0x2E

# control register
LIS2DH12_CTRL_REG1 = 0x20
LIS2DH12_CTRL_REG2 = 0x21
LIS2DH12_CTRL_REG3 = 0x22
LIS2DH12_CTRL_REG4 = 0x23
LIS2DH12_CTRL_REG5 = 0x24
LIS2DH12_CTRL_REG6 = 0x25
LIS2DH12_REFERENCE_REG = 0x26
LIS2DH12_STATUS_REG = 0x27

# status register
LIS2DH12_STATUS_REG_AUX = 0x7

# interrupt register
LIS2DH12_INT1_CFG = 0x30
LIS2DH12_INT1_SRC = 0x31
LIS2DH12_INT1_THS = 0x32
LIS2DH12_INT1_DURATION = 0x33

LIS2DH12_INT2_CFG = 0x34
LIS2DH12_INT2_SRC = 0x35
LIS2DH12_INT2_THS = 0x36
LIS2DH12_INT2_DURATION = 0x37

LIS2DH12_WHO_AM_I = 0x0F

LIS2DH12_CLICK_CFG = 0x38
LIS2DH12_CLICK_SRC = 0x39
LIS2DH12_CLICK_THS = 0x3A
LIS2DH12_TIME_LIMIT = 0x3B
LIS2DH12_TIME_LATENCY = 0x3C
LIS2DH12_TIME_WINDOW = 0x3D

STANDARD_GRAVITY = 9.806

# types of interrupt
# single click
X_SINGLE_CLICK_INT = 0x01
Y_SINGLE_CLICK_INT = 0x04
Z_SINGLE_CLICK_INT = 0x10
XYZ_SINGLE_CLICK_INT = 0x15
# double click
X_DOUBLE_CLICK_INT = 0x02
Y_DOUBLE_CLICK_INT = 0x08
Z_DOUBLE_CLICK_INT = 0x20
XYZ_DOUBLE_CLICK_INT = 0x2A
# move int
POSI_CHANGE_RECOGNIZE = 0xFF
X_POSI_CHANGE_RECOGNIZE = 0x83
Y_POSI_CHANGE_RECOGNIZE = 0x8C
Z_POSI_CHANGE_RECOGNIZE = 0xB0
MOVE_RECOGNIZE = 0x7F
X_MOVE_RECOGNIZE = 0x03
Y_MOVE_RECOGNIZE = 0x0C
Z_MOVE_RECOGNIZE = 0x30
# free fall int
FF_RECOGNIZE = 0x95  #and zl yl xl


class lis2dh12(object):
    '''
    lis2dh12 class
    API：sensor_reset(),process_xyz(),int_processing_data(),resolution,
    int_enable(int_type,int_ths,time_limit,time_latency,duration),read_acceleration
    '''
    def __init__(self, i2c_dev, int_pin, slave_address=0x19):
        '''
        :param i2c_dev: i2c object
        :param int_pin: gpio of pin which is connected with int1_pin
        :param slave_address: device address
        '''
        self._address = slave_address
        self._i2c_dev = i2c_dev
        self._int_pin = int_pin
        self._extint = None
        self._sensor_init()

    def _read_data(self, regaddr, datalen):
        '''
        i2c read data
        :param regaddr: register address
        :param datalen: length of reading data
        :return: data
        '''
        r_data = bytearray(datalen)
        reg_addres = bytearray([regaddr])
        self._i2c_dev.read(self._address, reg_addres, 1, r_data, datalen, 1)
        ret_data = list(r_data)
        return ret_data

    def _write_data(self, regaddr, data):
        '''
        i2c write data
        :param regaddr: register address
        :param data: data to write
        '''
        addr = bytearray([regaddr])
        w_data = bytearray([data])
        self._i2c_dev.write(self._address, addr, len(addr), w_data, len(w_data))

    def sensor_reset(self):
        '''
        reset the sensor
        '''
        # 重置chip
        self._write_data(LIS2DH12_CTRL_REG5, 0x80)

        print('reboot already. {}'.format(self._read_data(LIS2DH12_CTRL_REG5,1)))
        utime.sleep_ms(100)
        r_data = self._read_data(LIS2DH12_WHO_AM_I, 1)
        while r_data[0] != 0x33:
            r_data = self._read_data(LIS2DH12_WHO_AM_I, 1)
            utime.sleep_ms(5)

    def _sensor_init(self):
        '''
        initialize the sensor
        '''
        self.sensor_reset()

        self._write_data(LIS2DH12_CTRL_REG1, 0x77)  # set ODR 400HZ ,enable XYZ.
        utime.sleep_ms(20)  # (7/ODR) = 18ms
        self._write_data(LIS2DH12_CTRL_REG4, 0x08)  # ±2g

        self._write_data(LIS2DH12_CLICK_CFG, 0)  # clear click_cfg
        self._write_data(LIS2DH12_INT1_CFG, 0)  # clear int1_cfg
        self._write_data(LIS2DH12_INT2_CFG, 0)  # clear int2_cfg

    def int_enable(self,int_type,int_ths=0x12,time_limit=0x18,time_latency=0x12,time_window=0x55,duration=0x03):
        '''
        interrupt enable
        :param int_type: type of interrupt
        :param int_ths: threshold
        :param time_limit: click_int to send this parameter, time window limit
        :param time_latency: click_int to send this parameter, set the time_latency
        :param duration:
        '''
        # single_click int
        if int_type in (XYZ_SINGLE_CLICK_INT, X_SINGLE_CLICK_INT, Y_SINGLE_CLICK_INT, Z_SINGLE_CLICK_INT):
            self._write_data(LIS2DH12_CTRL_REG2, 0x07)  # Enable high pass filter for click function
            self._write_data(LIS2DH12_CTRL_REG3, 0x80)  # Bind interrupt to INT1 pin, default high level is valid
            self._write_data(LIS2DH12_CTRL_REG5, 0x08)  # INT1 latch
            self._write_data(LIS2DH12_CLICK_CFG, int_type)  # enable click_int
            self._write_data(LIS2DH12_CLICK_THS, int_ths)  # set threshold
            self._write_data(LIS2DH12_TIME_LIMIT, time_limit)  # set time_limit
        # double_click int
        elif int_type in (XYZ_DOUBLE_CLICK_INT, X_DOUBLE_CLICK_INT, Y_DOUBLE_CLICK_INT, Z_DOUBLE_CLICK_INT):
            self._write_data(LIS2DH12_CTRL_REG2, 0x07)
            self._write_data(LIS2DH12_CTRL_REG3, 0x80)
            self._write_data(LIS2DH12_CTRL_REG5, 0x08)
            self._write_data(LIS2DH12_CLICK_CFG, int_type)
            self._write_data(LIS2DH12_CLICK_THS, int_ths)
            self._write_data(LIS2DH12_TIME_LIMIT, time_limit)
            self._write_data(LIS2DH12_TIME_LATENCY, time_latency)
            self._write_data(LIS2DH12_TIME_WINDOW, time_window)
        # int
        elif int_type in (MOVE_RECOGNIZE, X_MOVE_RECOGNIZE, Y_MOVE_RECOGNIZE, Z_MOVE_RECOGNIZE,POSI_CHANGE_RECOGNIZE,
                          X_POSI_CHANGE_RECOGNIZE,Y_POSI_CHANGE_RECOGNIZE,Z_POSI_CHANGE_RECOGNIZE,FF_RECOGNIZE):
            self._write_data(LIS2DH12_CTRL_REG2, 0x00)  # switch off the high pass filter
            self._write_data(LIS2DH12_CTRL_REG3, 0x40)
            self._write_data(LIS2DH12_CTRL_REG5, 0x08)
            self._write_data(LIS2DH12_INT1_CFG, int_type)  # enable 6d int
            self._write_data(LIS2DH12_INT1_THS, int_ths)
            self._write_data(LIS2DH12_INT1_DURATION, duration)  # set duration


    def start_sensor(self):
        '''
        start the sensor
        '''
        self._write_data(LIS2DH12_CTRL_REG1, 0x77)  # ODR 100HZ ,enable XYZ.
        utime.sleep_ms(20)  # (7/ODR) = 18ms

    def process_xyz(self):
        '''
        Read registers and convert x-axis, y-axis, and z-axis data
        :return: x,y,z data
        '''
        data = []
        ctl4 = self._read_data(LIS2DH12_CTRL_REG4, 1)[0]
        big_endian = ctl4 & 0x40
        # read xl,xh,yl,yh,zl,zh
        for i in range(6):
            r_data = self._read_data(LIS2DH12_OUT_X_L + i, 1)
            data.append(r_data[0])

        if big_endian:
            x = data[0] * 256 + data[1]
            y = data[2] * 256 + data[3]
            z = data[4] * 256 + data[5]
        else:
            x = data[1] * 256 + data[0]
            y = data[3] * 256 + data[2]
            z = data[5] * 256 + data[4]

        return (x, y, z)

    def int_processing_data(self):
        '''
        handle int_processing
        :return: x,y,z-axis acceleration
        '''
        acc = self.read_acceleration
        int_src = self._read_data(LIS2DH12_INT1_SRC,1)  # read INT1_SRC，clear interrupt request
        return acc

    @property
    def _resolution(self):
        """
        resolution range.
        :return: range_2_G, range_4_G, range_8_G,, range_16_G.
        """
        ctl4 = self._read_data(LIS2DH12_CTRL_REG4,1)[0]
        return (ctl4 >> 4) & 0x03

    @property
    def _acceleration(self):
        """
        x,y,z-axis acceleration
        :return: x,y,z-axis acceleration
        """
        divider = 1
        accel_range = self._resolution
        if accel_range == 3:        # range_16_G
            divider = 2048
        elif accel_range == 2:      # range_8_G
            divider = 4096
        elif accel_range == 1:      # range_4_G
            divider = 8192
        elif accel_range == 0:      # range_2_G
            divider = 16384

        x, y, z = self.process_xyz()

        x = x / divider
        y = y / divider
        z = z / divider

        if accel_range == 3:        # range_16_G
            print('range_16_G')
            x = x if x <= 16 else x - 32
            y = y if y <= 16 else y - 32
            z = z if z <= 16 else z - 32
        elif accel_range == 2:      # range_8_G
            print('range_8_G')
            x = x if x <= 8 else x - 16
            y = y if y <= 8 else y - 16
            z = z if z <= 8 else z - 16
        elif accel_range == 1:      # range_4_G
            print('range_4_G')
            x = x if x <= 4 else x - 8
            y = y if y <= 4 else y - 8
            z = z if z <= 4 else z - 8
        elif accel_range == 0:      # range_2_G
            print('range_2_G')
            x = x if x <= 2 else x - 4
            y = y if y <= 2 else y - 4
            z = z if z <= 2 else z - 4

        return (x, y, z)

    @property
    def read_acceleration(self):
        '''
        read acceleration
        :return: x,y,z-axis acceleration
        '''

        while 1:
            status = self._read_data(LIS2DH12_STATUS_REG,1)[0]
            xyzda = status & 0x08   # if xyz data exists, set 1
            xyzor = status & 0x80
            if not xyzda:
                continue
            else:
                x,y,z = self._acceleration
                return (x, y, z)


    def set_mode(self,mode):
        """
        set work mode
        :param mode: 0: High resolution mode; 1: Normal mode; 2: Low power mode;
        :return: None
        """
        if mode == 0:
            self._write_data(LIS2DH12_CTRL_REG1, 0x77)  # ODR 400HZ ,enable XYZ.
            self._write_data(LIS2DH12_CTRL_REG4, 0x08)  # ±2g， High resolution mode
        elif mode == 1:
            self._write_data(LIS2DH12_CTRL_REG1, 0x57)  # ODR 100HZ ,enable XYZ.
            self._write_data(LIS2DH12_CTRL_REG4, 0x08)  # ±2g， Normal mode
        elif mode == 2:
            self._write_data(LIS2DH12_CTRL_REG1, 0x8f)
            self._write_data(LIS2DH12_CTRL_REG4, 0x08)  # ±2g， Low power mode
        else:
            print("wrong mode.")

    def set_int_callback(self, cb):
        self._extint = ExtInt(self._int_pin, ExtInt.IRQ_FALLING, ExtInt.PULL_PU, cb)

