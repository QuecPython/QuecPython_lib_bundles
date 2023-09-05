from machine import Pin
import utime

'''
from machine import I2C

I2C_SLAVE_ADDR = 0x000
data = bytearray([0x0, 0x0])
i2c_obj = I2C(I2C.I2C0, I2C.STANDARD_MODE)
i2c_obj.read(I2C_SLAVE_ADDR, bytearray([0x0, 0x0]), 1, data, 2, 0)
print(data)
'''

class PL5NF001(object):

    def __init__(self):
        self.CLK = Pin(Pin.GPIO9, Pin.OUT, Pin.PULL_PU, 1) # PL5NF001 CLK
        self.DIO = Pin(Pin.GPIO8, Pin.OUT, Pin.PULL_PU, 1) # PL5NF001 DIO

    def delay_ms(self, ms):
        utime.sleep_ms(ms)

    def delay_us(self, num):
        # for i in range(num):
        #     pass
        pass

    def start_signal(self):
        self.CLK.write(1)
        self.DIO.write(1)
        self.delay_us(2)
        self.DIO.write(0)
        self.delay_us(2)
        self.CLK.write(0)
        self.delay_us(2)

    def stop_signal(self):
        self.CLK.write(0)
        self.DIO.write(0)
        self.delay_us(2)
        self.CLK.write(1)
        self.delay_us(2)
        self.DIO.write(1)
        self.delay_us(2)

    def ack(self):
        self.CLK.write(0)
        self.DIO.write(0)
        self.delay_us(2)
        self.CLK.write(1)
        self.delay_us(4)
        self.CLK.write(0)

    def nack(self):
        self.CLK.write(0)
        self.DIO.write(1)
        self.delay_us(2)
        self.CLK.write(1)
        self.delay_us(4)
        self.CLK.write(0)

    def wait_ack(self):
        self.DIO.setDirection(1)
        # self.DIO = Pin(Pin.GPIO9, Pin.IN, Pin.PULL_PU, 1)
        i = 0
        # self.delay_us(2)
        self.CLK.write(1)
        # self.delay_us(2)
        while (self.DIO.read()):
            i += 1
            if i > 2000:
                self.stop_signal()
                print('iic stop')
                return 1
        self.CLK.write(0)
        self.DIO.setDirection(0)
        # self.DIO = Pin(Pin.GPIO9, Pin.OUT, Pin.PULL_DISABLE, 1)
        return 0

    def write_data(self, data):
        j = 0
        self.CLK.write(0)
        for j in range(8):
            if data & 0x80:
                self.DIO.write(1)
            else:
                self.DIO.write(0)
            data <<= 1
            self.CLK.write(1)
            self.delay_us(2)
            self.CLK.write(0)
            self.delay_us(2)

    def read_byte(self, ack):
        self.DIO.setDirection(1)
        # self.DIO = Pin(Pin.GPIO9, Pin.IN, Pin.PULL_DISABLE, 1)
        recive = 0
        l = list()
        utime.sleep_ms(12)
        for i in range(0, 8):
            self.CLK.write(0)
            self.delay_us(2)
            self.CLK.write(1)
            self.delay_us(2)
            recive << 1
            level = self.DIO.read()
            l.append(level)
            if level == 1:
                recive | 1
            self.delay_us(2)
            if ack == 1:
                self.ack()
            else:
                self.nack()
        print('ReadByte Recive = {}'.format(recive))
        # print(l)
        self.DIO.setDirection(0)
        return recive


if __name__ == '__main__':
    # parse
    p = PL5NF001()
    p.start_signal()
    p.write_data(0x00)
    p.wait_ack()
    p.write_data(0x01)
    p.wait_ack()
    for i in range(81):
        p.read_byte(1)
    p.read_byte(0)
    #     # p.read_byte(0)
    # # p.read_byte(1)
    # # p.read_byte(1)
    p.stop_signal()


