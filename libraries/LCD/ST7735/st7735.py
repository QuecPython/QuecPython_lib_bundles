from machine import LCD
from usr.LCD import Peripheral_LCD
from usr import LCDPublic


class St7735(Peripheral_LCD):
    def __init__(self, InitData=None, width=128, height=160, clk=13000, dir=0):
        self._LcdInit(InitData, width, height, dir, clk)
        super().__init__(self)

    def _LcdInit(self, InitData, width, height, dir, clk):
        L2R_U2D = 0
        L2R_D2U = 1
        R2L_U2D = 2
        R2L_D2U = 3

        U2D_L2R = 4
        U2D_R2L = 5
        D2U_L2R = 6
        D2U_R2L = 7

        regval = 0
        if(dir == L2R_U2D):
            regval |= (0 << 7) | (0 << 6) | (0 << 5)
        elif dir == L2R_D2U:
            regval |= (1 << 7) | (0 << 6) | (0 << 5)
        elif dir == R2L_U2D:
            regval |= (0 << 7) | (1 << 6) | (0 << 5)
        elif dir == R2L_D2U:
            regval |= (1 << 7) | (1 << 6) | (0 << 5)
        elif dir == U2D_L2R:
            regval |= (0 << 7) | (0 << 6) | (1 << 5)
        elif dir == U2D_R2L:
            regval |= (0 << 7) | (1 << 6) | (1 << 5)
        elif dir == D2U_L2R:
            regval |= (1 << 7) | (0 << 6) | (1 << 5)
        elif dir == D2U_R2L:
            regval |= (1 << 7) | (1 << 6) | (1 << 5)
        else:
            regval |= (0 << 7) | (0 << 6) | (0 << 5)

        self._lcd_w = width
        self._lcd_h = height

        if(regval & 0X20):
            if(width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if(width > height):
                self._lcd_w = height
                self._lcd_h = width

        init_data = (
            0, 0, 0x11,
            2, 0, 120,

            0, 3, 0xb1,
            1, 1, 0x01,
            1, 1, 0x08,
            1, 1, 0x05,

            0, 3, 0xb2,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,

            0, 6, 0xb3,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,

            0, 1, 0xb4,
            1, 1, 0x03,

            0, 3, 0xc0,
            1, 1, 0x28,
            1, 1, 0x08,
            1, 1, 0x04,

            0, 1, 0xc1,
            1, 1, 0xc0,

            0, 2, 0xc2,
            1, 1, 0x0d,
            1, 1, 0x00,

            0, 2, 0xc3,
            1, 1, 0x8d,
            1, 1, 0x2a,

            0, 2, 0xc4,
            1, 1, 0x8d,
            1, 1, 0xee,

            0, 1, 0xc5,
            1, 1, 0x12,

            0, 1, 0x36,
            1, 1, regval,

            0, 16, 0xe0,
            1, 1, 0x04,
            1, 1, 0x22,
            1, 1, 0x07,
            1, 1, 0x0a,
            1, 1, 0x2e,
            1, 1, 0x30,
            1, 1, 0x25,
            1, 1, 0x2a,
            1, 1, 0x28,
            1, 1, 0x26,
            1, 1, 0x2e,
            1, 1, 0x3a,
            1, 1, 0x00,
            1, 1, 0x01,
            1, 1, 0x03,
            1, 1, 0x13,

            0, 16, 0xe1,
            1, 1, 0x04,
            1, 1, 0x16,
            1, 1, 0x06,
            1, 1, 0x0d,
            1, 1, 0x2d,
            1, 1, 0x26,
            1, 1, 0x23,
            1, 1, 0x27,
            1, 1, 0x27,
            1, 1, 0x25,
            1, 1, 0x2d,
            1, 1, 0x3b,
            1, 1, 0x00,
            1, 1, 0x01,
            1, 1, 0x04,
            1, 1, 0x13,

            0, 1, 0x3a,
            1, 1, 0x05,

            0, 1, 0x35,
            1, 1, 0x00,

            0, 0, 0x29,
            1, 0, 0x2c,
        )
        lcd_set_display_area = (
            0, 4, 0x2a,
            1, 1, LCDPublic.XSTART_H,
            1, 1, LCDPublic.XSTART_L,
            1, 1, LCDPublic.XEND_H,
            1, 1, LCDPublic.XEND_L,
            0, 4, 0x2b,
            1, 1, LCDPublic.YSTART_H,
            1, 1, LCDPublic.YSTART_L,
            1, 1, LCDPublic.YEND_H,
            1, 1, LCDPublic.YEND_L,
            0, 0, 0x2c,
        )
        lcd_display_on = (
            0, 0, 0x11,
            2, 0, 20,
            0, 0, 0x29,
        )
        lcd_display_off = (
            0, 0, 0x28,
            2, 0, 120,
            0, 0, 0x10,
        )
        if InitData is None:
            self._initData = bytearray(init_data)
        else:
            self._initData = InitData

        self._invalidData = bytearray(lcd_set_display_area)
        self._displayOn = bytearray(lcd_display_on)
        self._displayOff = bytearray(lcd_display_off)

        self._lcd = LCD()
        self._lcd.lcd_init(
            self._initData,
            self._lcd_w,
            self._lcd_h,
            clk,
            1,
            4,
            0,
            self._invalidData,
            self._displayOn,
            self._displayOff,
            None)


'''
Due to the characteristics of Python language (slower execution than C language), 
the best scheme is to use LCD combined with lvgl.
'''
if __name__ == '__main__':

    lcd_test = St7735()
    lcd_test.ShowAsciiStr(10, 10, 16, 24, 'QUECTEL', 0xf800, 0x001f)
