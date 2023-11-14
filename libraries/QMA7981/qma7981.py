# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
File: i2c_qma7981.py
Project: i2c
File Created: Sunday, 11th March 2022 3:51:22 pm
Author: elian.wang

-----
Copyright 2022 - 2022 quectel
'''


from machine import I2C
from machine import ExtInt
from machine import Pin
#from machine import I2C_simulation
import utime as time

# TODO:AD0脚LSB of I2C address, or SDO of 4WSPI 当AD0接地时 IIC从机地址为0x12，当AD0接到VDDIO时从机地址为0x13；
# TODO：IIC支持快速和标准模式，100kHz到400kHz


class qma7981():
    i2c_log = None
    i2c_dev = None
    i2c_addre = 0x12
    step = None
    acc = [0, 0, 0]

    # 中断类型
    SIG_MOT_INT = 0
    ANY_MOT_INT_X = 1
    ANY_MOT_INT_Y = 2
    ANY_MOT_INT_Z = 3
    NO_MOT_INT = 4
    HAND_RAISE_INT = 5
    HAND_DOWN_INT = 6
    STEP_INT = 7

    IRQ_RISING = 0
    IRQ_FALLING = 1

    PM_ADDR = 0x11
    STEP_CFG_ADDR = 0x12
    STEP_CLR_ADDR = 0x13
    # X轴加速度
    ACC_X_L_ADDR = 0x01
    ACC_X_H_ADDR = 0x02
    # Y轴加速度
    ACC_Y_L_ADDR = 0x03
    ACC_Y_H_ADDR = 0x04
    # Z轴加速度
    ACC_Z_L_ADDR = 0x05
    ACC_Z_H_ADDR = 0x06
    # step count
    STEPCNT_L_ADDR = 0x07
    STEPCNT_M_ADDR = 0x08
    STEPCNT_H_ADDR = 0x0E
    #获取触发any mot中断的动作方向
    INT_ST0_ADDR = 0x09
    # 加速度计算单位设置
    FSR_REG_ADDR = 0x0F

    STEP_SAMPLE_CNT_ADDR = 0x12
    STEP_PRECISION_ADDR = 0x13
    STEP_TIME_LOW_ADDR = 0x14
    STEP_TIME_UP_ADDR = 0x15
    # 中断使能
    INT_EN0_ADDR = 0x16
    INT_EN1_ADDR = 0x17
    INT_EN2_ADDR = 0x18
    # 中断map
    INT_MAP0_ADDR = 0x19
    INT_MAP1_ADDR = 0x1A
    INT_MAP2_ADDR = 0x1B
    INT_MAP3_ADDR = 0x1C
    # 中断引脚配置
    INTPIN_CONF_ADDR = 0x20
    INT_CFG_ADDR = 0x21

    RAISE_WAKE_ADDR = 0x2A
    DOWN_WAKE_ADDR = 0x2B
    MOT_CONF0_ADDR = 0x2C
    NO_MOT_TH_ADDR = 0x2D
    # 任意方向震动中断触发值寄存器
    ANY_MOT_TH_ADDR = 0x2E
    SIG_MOT_CONF_ADDR = 0x2F
    RAISE_WAKE_PERIOD_ADDR = 0x35
    

    def _write(self, reg_addr, data):
        self.i2c_dev.write(self.i2c_addre,
                           bytearray(reg_addr), 1,
                           bytearray(data), len(data))

    def _read(self, reg_addr, length):
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        ret = self.i2c_dev.read(self.i2c_addre,
                          bytearray(reg_addr), 1,
                          r_data, length,
                          0)
        if ret == -1:
            return []
        else:
            return list(r_data)

    def __init__(self, user_cb, INT1=None, INT2=None, INT1_output_mode=1, INT2_output_mode=1):
        self.cb = user_cb
        self.i2c_dev = I2C(I2C.I2C0, I2C.FAST_MODE)  # 返回i2c对象
        self.event = None
        self.data = None
        self.gpio_set_state = 0 # gpio设置的状态，用于分配中断对应引脚
        # set device into active mode
        self._write([self.PM_ADDR], [0xC0])
        if INT1 != None:
            if INT1_output_mode == 0:
                self.extint = ExtInt(INT1, ExtInt.IRQ_RISING, ExtInt.PULL_PD, self.ext_cb)
                data = self._read([self.INTPIN_CONF_ADDR], 1)
                data[0] |= 0x01
                print('INTPIN_CONF_ADDR: {}'.format(data))
                self._write([self.INTPIN_CONF_ADDR], [data[0]])
            elif INT1_output_mode == 1:
                self.extint = ExtInt(INT1, ExtInt.IRQ_FALLING, ExtInt.PULL_PU, self.ext_cb)
                data = self._read([self.INTPIN_CONF_ADDR], 1)
                data[0] &= 0xFE
                print('INTPIN_CONF_ADDR: {}'.format(data))
                self._write([self.INTPIN_CONF_ADDR], [data[0]])
            else:
                raise Exception('set gpio1 trigger mode fault')
            self.extint.enable()
        if INT2 != None:
            if INT2_output_mode == 0:
                self.extint = ExtInt(INT2, ExtInt.IRQ_RISING , ExtInt.PULL_PD , self.ext_cb)
                data = self._read([self.INTPIN_CONF_ADDR], 1)
                data[0] |= 0x04
                print('INTPIN_CONF_ADDR: {}'.format(data))
                self._write([self.INTPIN_CONF_ADDR], [data[0]])
            elif INT2_output_mode == 1:
                data = self._read([self.INTPIN_CONF_ADDR], 1)
                data[0] &= 0xFB
                print('INTPIN_CONF_ADDR: {}'.format(data))
                self._write([self.INTPIN_CONF_ADDR], [data[0]])
                self.extint = ExtInt(INT2, ExtInt.IRQ_FALLING, ExtInt.PULL_PU, self.ext_cb)
            else:
                raise Exception('set gpio2 trigger mode fault')
            self.extint.enable()
        if INT1 != None and INT2 != None:
            self.gpio_set_state = 3
        elif INT1 != None:
            self.gpio_set_state = 1
        elif INT2 != None:
            self.gpio_set_state = 2

        self._write([self.FSR_REG_ADDR], [0xF8])
        # interrupt is in latch mode
        self._write([self.INT_CFG_ADDR], [0x1F])
        time.sleep_ms(10) 

    def ext_cb(self, args):
        data = self._read([self.INT_ST0_ADDR], 3)
        direction = data[0] & 0x08
        print('state {}'.format(data))
        if data[1] & 0x01:
            self.event = self.SIG_MOT_INT # significant interrupt is active
        elif data[0] & 0x01:
            self.event = self.ANY_MOT_INT_X # any_motion interrupt is triggered by X
        elif data[0] & 0x02:
            self.event = self.ANY_MOT_INT_Y # any_motion interrupt is triggered by Y
        elif data[0] & 0x04:
            self.event = self.ANY_MOT_INT_Z # any_motion interrupt is triggered by Z
        elif data[0] & 0x80:
            self.event = self.NO_MOT_INT # no_motion interrupt is triggered
        elif data[1] & 0x02:
            self.event = self.HAND_RAISE_INT # raise hand interrupt is active
        elif data[1] & 0x04:
            self.event = self.HAND_DOWN_INT # hand down interrupt is active
        elif data[1] & 0x08:
            self.event = self.STEP_INT # step interrupt is active
        if data[0] & 0x07 or data[1] & 0x01:
            self.data = self.readacc()
            print('acc {}'.format(self.data))
        elif data[1] & 0x48:
            self.data = self.readstep()
            print('step {}'.format(self.readstep))
        self.cb(self.event, self.data)
    
    def set_any_motion_intr(self, en, threshod=0, sample_times=1):
        if en == True:
            # set any motion interrupt consecutive times 
            data = self._read([self.MOT_CONF0_ADDR], 1)
            data[0] &= 0xFC
            if sample_times <= 3:
                data[0] |= sample_times 
            else:
                data[0] |= 0x01 # 2 times
            self._write([self.MOT_CONF0_ADDR], [data[0]]) 
            # set the full of accelerometer 0xF8==>Acceleration range:16g; Resolution:1.95mg/LSB
            self._write([self.FSR_REG_ADDR], [0xF8])
            # set any motion interrupt threshod value 
            threshod = threshod // 31 # 1.95mg * 16
            print('threshod{}'.format(threshod))
            self._write([self.ANY_MOT_TH_ADDR], [threshod]) # 16 / bits
            self._write([self.SIG_MOT_CONF_ADDR], [0x00])
            # 使能中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] |= 0x07
            print('intr_en{}'.format(intr_en))
            self._write([self.INT_EN2_ADDR], [intr_en[0]])
            # 设置中断脚
            if self.gpio_set_state & 0x01:
                intr_map = self._read([self.INT_MAP1_ADDR], 1)
                intr_map[0] |= 0x01
                print('intr_map{}'.format(intr_map))
                self._write([self.INT_MAP1_ADDR], [intr_map[0]])
            elif self.gpio_set_state & 0x02:
                intr_map = self._read([self.INT_MAP3_ADDR], 1)
                intr_map[0] |= 0x01
                self._write([self.INT_MAP3_ADDR], [intr_map[0]])
        else:
            # 取消中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] &= 0xF8
            self._write([self.INT_EN2_ADDR], [intr_en[0]])

    def set_sig_motion_intr(self, en, threshod=0,  sample_times=1, axis_direction=0):
        if en == True:
            # set any motion interrupt consecutive times 
            data = self._read([self.MOT_CONF0_ADDR], 1)
            data[0] &= 0xFC
            if sample_times <= 3:
                data[0] |= sample_times 
            else:
                data[0] |= 0x01 # 2 times
            self._write([self.MOT_CONF0_ADDR], [data[0]]) 
            # set the full of accelerometer 0xF8==>Acceleration range:16g; Resolution:1.95mg/LSB
            self._write([self.FSR_REG_ADDR], [0xF8])
            # set any motion interrupt threshod value 
            threshod = threshod // 31 # 1.95mg * 16
            self._write([self.ANY_MOT_TH_ADDR], [threshod]) # 16 / bits
            self._write([self.SIG_MOT_CONF_ADDR], [0x01])
            # 使能中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] &= 0xF8
            if axis_direction == 0:
                intr_en[0] |= 0x01
            elif axis_direction == 1:
                intr_en[0] |= 0x02
            elif axis_direction == 2:
                intr_en[0] |= 0x04
            print('intr_en{}'.format(intr_en))
            self._write([self.INT_EN2_ADDR], [intr_en[0]])
            # 设置中断脚
            if self.gpio_set_state & 0x01:
                intr_map = self._read([self.INT_MAP0_ADDR], 1)
                intr_map[0] |= 0x01
                self._write([self.INT_MAP0_ADDR], [intr_map[0]])
            elif self.gpio_set_state & 0x02:
                intr_map = self._read([self.INT_MAP2_ADDR], 1)
                intr_map[0] |= 0x01
                self._write([self.INT_MAP2_ADDR], [intr_map[0]])
        else:
            # 取消中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] &= 0xF8
            self._write([self.INT_EN2_ADDR], [intr_en[0]])
    
    def set_no_motion_intr(self, en, threshod, duration_time = 10, axis_direction=0x03):
        if en == True:
           # set no motion interrupt consecutive times 
            data = self._read([self.MOT_CONF0_ADDR], 1)
            data[0] &= 0x03
            data[0] |= (duration_time << 2)
            print('MOT_CONF0_ADDR:{}'.format(data))
            self._write([self.MOT_CONF0_ADDR], [data[0]]) 
            # set no motion interrupt threshod value 
            threshod = threshod // 31 # 1.95mg * 16
            self._write([self.NO_MOT_TH_ADDR], [threshod]) # 16 / bits
            self._write([self.SIG_MOT_CONF_ADDR], [0x01])
            # 使能中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] &= 0x1F
            if axis_direction & 0x01:
                intr_en[0] |= 0x20
            if axis_direction & 0x02:
                intr_en[0] |= 0x40
            if axis_direction & 0x04:
                intr_en[0] |= 0x80
            print('INT_EN2_ADDR:{}'.format(intr_en))
            self._write([self.INT_EN2_ADDR], [intr_en[0]])
            # 设置中断脚
            if self.gpio_set_state & 0x01:
                intr_map = self._read([self.INT_MAP1_ADDR], 1)
                intr_map[0] |= 0x80
                self._write([self.INT_MAP1_ADDR], [intr_map[0]])
            elif self.gpio_set_state & 0x02:
                intr_map = self._read([self.INT_MAP3_ADDR], 1)
                intr_map[0] |= 0x80
                self._write([self.INT_MAP3_ADDR], [intr_map[0]])
        else:
            # 取消中断
            intr_en = self._read([self.INT_EN2_ADDR], 1)
            intr_en[0] &= 0x1F
            self._write([self.INT_EN2_ADDR], [intr_en[0]])


    def set_step_intr(self, intr_type, en, threshod=0, axis_direction = 0):
        if en == True:
            # enable step counter
            self._write([self.STEP_CFG_ADDR], [0x8C])
            # 使能中断
            intr_en = self._read([self.INT_EN0_ADDR], 1)
            intr_en[0] |= 0x08
            print('intr_en{}'.format(intr_en))
            self._write([self.INT_EN0_ADDR], [intr_en[0]])
            # 设置中断脚
            if self.gpio_set_state & 0x02:
                intr_map = self._read([self.INT_MAP2_ADDR], 1)
                intr_map[0] |= 0x08
                print('intr_map{}'.format(intr_map))
                self._write([self.INT_MAP2_ADDR], [intr_map[0]])
            elif self.gpio_set_state & 0x01:
                intr_map = self._read([self.INT_MAP0_ADDR], 1)
                intr_map[0] |= 0x08
                print('intr_map{}'.format(intr_map))
                self._write([self.INT_MAP0_ADDR], [intr_map[0]])
        else:
            # 取消中断
            intr_en = self._read([self.INT_EN0_ADDR], 1)
            intr_en[0] &= 0xF7
            self._write([self.INT_EN2_ADDR], [intr_en[0]])
    
    def set_raise_intr(self, en, wake_sum_th=10, wake_diff_th=1.0):
        if en:
            if wake_sum_th and wake_diff_th!=0 and wake_diff_th < 1.2:
                wake_sum_th = int(wake_sum_th * 2)
                wake_diff_th = int((wake_diff_th - 0.2)*10)
                data = (wake_sum_th & 0x3F) | ((wake_diff_th & 0x03)<<6)
                print('RAISE_WAKE_ADDR:{}'.format(data))
                self._write([self.RAISE_WAKE_ADDR], [data])

                data = wake_diff_th >> 2
                read_data = self._read([self.DOWN_WAKE_ADDR], 1)
                data = (read_data[0] & 0xFC) | data
                print('DOWN_WAKE_ADDR:{}'.format(data))
                self._write([self.DOWN_WAKE_ADDR], [data])

            # 使能中断
                intr_en = self._read([self.INT_EN0_ADDR], 1)
                intr_en[0] |= 0x02
                print('intr_en{}'.format(intr_en))
                self._write([self.INT_EN0_ADDR], [intr_en[0]])
        
            # 设置中断脚
            if self.gpio_set_state & 0x02:
                intr_map = self._read([self.INT_MAP2_ADDR], 1)
                intr_map[0] |= 0x02
                print('intr_map INT_MAP2_ADDR:{}'.format(intr_map))
                self._write([self.INT_MAP2_ADDR], [intr_map[0]])
            elif self.gpio_set_state & 0x01:
                intr_map = self._read([self.INT_MAP0_ADDR], 1)
                intr_map[0] |= 0x02
                print('intr_map INT_MAP0_ADDR:{}'.format(intr_map))
                self._write([self.INT_MAP0_ADDR], [intr_map[0]])
        else:
            intr_en = self._read([self.INT_EN0_ADDR], 1)
            intr_en[0] &= 0xFD
            print('intr_en{}'.format(intr_en))
            self._write([self.INT_EN0_ADDR], [intr_en[0]])
        
    def readstep(self):
        data0 = self._read([self.STEPCNT_L_ADDR], 1)
        data1 = self._read([self.STEPCNT_M_ADDR], 1)
        data2 = self._read([self.STEPCNT_H_ADDR], 1)
        if data0[0] != -1 and data1[0] != -1 and data2[0] != -1:
            self.step = (data2[0] << 8) | (data1[0] << 8) | data0[0]
        return self.step

    def readacc(self):
        data = self._read([self.ACC_X_L_ADDR], 6)
        print('acc data{}'.format(data))
    
        if len(data) != 0:
            if data[1] & 0x80:
                self.acc[0] = (0x4000 - ((data[0]|(data[1]<<8)) >> 2)) * -1.95
            else:
                self.acc[0] = ((data[0]|(data[1]<<8)) >> 2) * 1.95 # 根据数据QMA7981_FSR_REG寄存器计算
            if data[3] & 0x80:
                self.acc[1] = (0x4000 - ((data[2]|(data[3]<<8)) >> 2)) * -1.95
            else:
                self.acc[1] = ((data[2]|(data[3]<<8)) >> 2) * 1.95 # 根据数据QMA7981_FSR_REG寄存器计算
            if data[5] & 0x80:
                self.acc[2] = (0x4000 - ((data[4]|(data[5]<<8)) >> 2)) * -1.95
            else:
                self.acc[2] = ((data[4]|(data[5]<<8)) >> 2) * 1.95 # 根据数据QMA7981_FSR_REG寄存器计算
            print('acc value{}'.format(self.acc))
        return self.acc

    def read_sta_reg(self):
        data = qma7981_dev._read([qma7981_dev.INT_ST0_ADDR], 3)
        print('INT_ST0:{}'.format(data))
        data = qma7981_dev._read([qma7981_dev.INT_EN0_ADDR], 3)
        print('INT_EN0:{}'.format(data))
        data = qma7981_dev._read([qma7981_dev.INT_MAP0_ADDR], 4)
        print('INT_MAP0:{}'.format(data))
        data = self._read([self.ACC_X_L_ADDR], 6)
        print('acc data{}'.format(data))
        data = qma7981_dev._read([qma7981_dev.INTPIN_CONF_ADDR], 1)
        print('INTPIN_CONF_ADDR:{}'.format(data))

    def clearstep(self):
        self._write([self.STEP_CLR_ADDR], [0xFF])
        

qma7981_dev = None

def user_cb_test(event, data):
    if event == qma7981.SIG_MOT_INT:
        print("significant interrupt is active")
    elif event == qma7981.ANY_MOT_INT_X:
        print("any_motion interrupt is triggered by X")
    elif event == qma7981.ANY_MOT_INT_Y:
        print("any_motion interrupt is triggered by Y")
    elif event == qma7981.ANY_MOT_INT_Z:
        print("any_motion interrupt is triggered by Z")
    elif event == qma7981.NO_MOT_INT:
        print("no_motion interrupt is triggered")
    elif event == qma7981.HAND_RAISE_INT:
        print("raise hand interrupt is active")
    elif event == qma7981.HAND_DOWN_INT:
        print("hand down interrupt is active")
    elif event == qma7981.HAND_DOWN_INT:
        print("hand down interrupt is active")
    print('get value  {}'.format(data))

if __name__ == "__main__":
    print('start')
    # GPIO7 GPIO33
    qma7981_dev = qma7981(user_cb_test, INT1=ExtInt.GPIO33, INT1_output_mode=qma7981.IRQ_FALLING)
    qma7981_dev.set_any_motion_intr(True, threshod=200, sample_times=1)
    for i in range(100):
        qma7981_dev.readacc()
        time.sleep(1)