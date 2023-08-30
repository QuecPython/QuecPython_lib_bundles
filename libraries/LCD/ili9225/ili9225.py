from machine import LCD
from usr.LCD import Peripheral_LCD
from usr import LCDPublic


class Ili9225(Peripheral_LCD):
    def __init__(self, InitData=None, width=176, height=220, clk=13000, dir=0):
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
            regval |= (1 << 5) | (1 << 4) | (0 << 3)
        elif dir == L2R_D2U:
            regval |= (0 << 5) | (1 << 4) | (0 << 3)
        elif dir == R2L_U2D:
            regval |= (1 << 5) | (0 << 4) | (0 << 3)
        elif dir == R2L_D2U:
            regval |= (0 << 5) | (0 << 4) | (0 << 3)
        elif dir == U2D_L2R:
            regval |= (1 << 5) | (1 << 4) | (1 << 3)
        elif dir == U2D_R2L:
            regval |= (1 << 5) | (0 << 4) | (1 << 3)
        elif dir == D2U_L2R:
            regval |= (0 << 5) | (1 << 4) | (1 << 3)
        elif dir == D2U_R2L:
            regval |= (0 << 5) | (0 << 4) | (1 << 3)
        else:
            regval |= (1 << 5) | (1 << 4) | (0 << 3)

        self._lcd_w = width
        self._lcd_h = height

        if(regval & 0X04):
            if(width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if(width > height):
                self._lcd_w = height
                self._lcd_h = width

        init_data = (
            2, 0, 120,
            0, 1, 0x02,
            1, 2, 0x01, 0x00,
            0, 1, 0x01,
            1, 2, 0x01, 0x1C,
            0, 1, 0x03,
            1, 2, 0x10, regval,
            0, 1, 0x08,
            1, 2, 0x08, 0x08,
            0, 1, 0x0B,
            1, 2, 0x11, 0x00,
            0, 1, 0x0C,
            1, 2, 0x00, 0x00,
            0, 1, 0x0F,
            1, 2, 0x14, 0x01,
            0, 1, 0x15,
            1, 2, 0x00, 0x00,
            0, 1, 0x20,
            1, 2, 0x00, 0x00,
            0, 1, 0x21,
            1, 2, 0x00, 0x00,
            0, 1, 0x10,
            1, 2, 0x08, 0x00,
            0, 1, 0x11,
            1, 2, 0x1F, 0x3F,
            0, 1, 0x12,
            1, 2, 0x01, 0x21,
            0, 1, 0x13,
            1, 2, 0x00, 0x0F,
            0, 1, 0x14,
            1, 2, 0x43, 0x49,
            0, 1, 0x30,
            1, 2, 0x00, 0x00,
            0, 1, 0x31,
            1, 2, 0x00, 0xDB,
            0, 1, 0x32,
            1, 2, 0x00, 0x00,
            0, 1, 0x33,
            1, 2, 0x00, 0x00,
            0, 1, 0x34,
            1, 2, 0x00, 0xDB,
            0, 1, 0x35,
            1, 2, 0x00, 0x00,
            0, 1, 0x36,
            1, 2, 0x00, 0xAF,
            0, 1, 0x37,
            1, 2, 0x00, 0x00,
            0, 1, 0x38,
            1, 2, 0x00, 0xDB,
            0, 1, 0x39,
            1, 2, 0x00, 0x00,
            0, 1, 0x50,
            1, 2, 0x00, 0x01,
            0, 1, 0x51,
            1, 2, 0x20, 0x0B,
            0, 1, 0x52,
            1, 2, 0x00, 0x00,
            0, 1, 0x53,
            1, 2, 0x04, 0x04,
            0, 1, 0x54,
            1, 2, 0x0C, 0x0C,
            0, 1, 0x55,
            1, 2, 0x00, 0x0C,
            0, 1, 0x56,
            1, 2, 0x01, 0x01,
            0, 1, 0x57,
            1, 2, 0x04, 0x00,
            0, 1, 0x58,
            1, 2, 0x11, 0x08,
            0, 1, 0x59,
            1, 2, 0x05, 0x0C,
            0, 1, 0x07,
            1, 2, 0x10, 0x17,
            0, 1, 0x22,
        )
        lcd_set_display_area = (
            0, 1, 0x36,
            1, 2, LCDPublic.XEND,
            0, 1, 0x37,
            1, 2, LCDPublic.XSTART,
            0, 1, 0x38,
            1, 2, LCDPublic.YEND,
            0, 1, 0x39,
            1, 2, LCDPublic.YSTART,
            0, 1, 0x20,
            1, 2, LCDPublic.XSTART,
            0, 1, 0x21,
            1, 2, LCDPublic.YSTART,
            0, 1, 0x22,
        )
        lcd_display_on = (
            0, 1, 0x07,
            1, 2, 0x10, 0x17,
        )
        lcd_display_off = (
            0, 1, 0x07,
            1, 2, 0x10, 0x04,
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

    lcd_test = Ili9225()
    lcd_test.ShowAsciiStr(10, 10, 16, 24, 'QUECTEL', 0xf800, 0x001f)
