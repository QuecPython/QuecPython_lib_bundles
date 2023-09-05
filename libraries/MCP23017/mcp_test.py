from machine import I2C
from usr import mcp23017
import utime

if __name__=="__main__":
    print("begin... ")

    i2c = I2C(I2C.I2C1, I2C.STANDARD_MODE)
    mcp = mcp23017.Mcp23017(i2c, address=0x20)
    mcp.pin(0, mode=1)
    mcp.pin(1, mode=1, pullup=True)
    mcp.pin(1)
    mcp.pin(2, mode=0, value=1)
    mcp.pin(3, mode=0, value=0)

    '''
        mcp.mode = 0x0000
        for n in range(100):
            if n % 2 == 0:
            #for i in range(15):
                mcp.gpio = 0x0000
            else:
                mcp.gpio = 0xFFFF
            utime.sleep_ms(100)

        # list interface
        #mcp[0].input()
        #mcp[1].input(pull=1)
        #mcp[1].value()
        mcp[i].output(0)
        utime.sleep_ms(10)
        mcp[i].output(1)
        utime.sleep_ms(10)

        # method interface
        mcp.pin(0, mode=1)
        mcp.pin(1, mode=1, pullup=True)
        mcp.pin(1)
        mcp.pin(2, mode=0, value=1)
        mcp.pin(3, mode=0, value=0)

        mcp.config(interrupt_polarity=0, interrupt_mirror=1)  

        # property interface 16-bit
        mcp.mode = 0xfffe
        mcp.gpio = 0x0001

        # property interface 8-bit
        mcp.porta.mode = 0xfe
        mcp.portb.mode = 0xff
        mcp.porta.gpio = 0x01
        mcp.portb.gpio = 0x02
    '''