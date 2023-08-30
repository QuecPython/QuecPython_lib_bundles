from machine import LCD
from usr.LCD import Peripheral_LCD
from usr import LCDPublic

class Ili9341(Peripheral_LCD):
    def __init__(self, InitData=None, width=320, height=240, clk=13000,dir=0): 
        self._LcdInit(InitData, width, height, dir,clk)
        super().__init__(self)

    def _LcdInit(self, InitData,width,height,dir,clk):
        L2R_U2D = 0
        L2R_D2U = 1
        R2L_U2D = 2
        R2L_D2U = 3

        U2D_L2R = 4
        U2D_R2L = 5
        D2U_L2R = 6
        D2U_R2L = 7

        regval = 1 << 3
        if(dir == L2R_U2D):
            regval |= (0<<7)|(0<<6)|(0<<5)
        elif dir == L2R_D2U:
            regval |= (1<<7)|(0<<6)|(0<<5)
        elif dir == R2L_U2D:
            regval |= (0<<7)|(1<<6)|(0<<5)
        elif dir == R2L_D2U:
            regval |= (1<<7)|(1<<6)|(0<<5)
        elif dir == U2D_L2R:
            regval |= (0<<7)|(0<<6)|(1<<5)
        elif dir == U2D_R2L:
            regval |= (0<<7)|(1<<6)|(1<<5)
        elif dir == D2U_L2R:
            regval |= (1<<7)|(0<<6)|(1<<5)
        elif dir == D2U_R2L:
            regval |= (1<<7)|(1<<6)|(1<<5)
        else:
            regval |= (0<<7)|(0<<6)|(0<<5)

         
        self._lcd_w = width
        self._lcd_h = height
        if(regval&0X20):
            if(width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if(width > height):
                self._lcd_w = height
                self._lcd_h = width

        init_data = (
            2, 0, 120,
            0,3,0xCF,  
            1,1,0x00, 
            1,1,0xD9,
            1,1,0X30, 
            0,4,0xED,  
            1,1,0x64, 
            1,1,0x03, 
            1,1,0X12, 
            1,1,0X81, 
            0,3,0xE8,  
            1,1,0x85, 
            1,1,0x10, 
            1,1,0x7A, 
            0,5,0xCB,  
            1,1,0x39, 
            1,1,0x2C, 
            1,1,0x00, 
            1,1,0x34, 
            1,1,0x02, 
            0,1,0xF7,  
            1,1,0x20, 
            0,2,0xEA,  
            1,1,0x00, 
            1,1,0x00, 
            0,1,0xC0, 
            1,1,0x1B,  
            0,1,0xC1,
            1,1,0x12,
            0,2,0xC5,
            1,1,0x08,
            1,1,0x26,
            0,1,0xC7,
            1,1,0XB7, 
            0,1,0x36,
            1,1,regval, 
            0,1,0x3A,   
            1,1,0x55, 
            0,2,0xB1,   
            1,1,0x00,   
            1,1,0x1A, 
            0,2,0xB6,
            1,1,0x0A, 
            1,1,0xA2, 
            0,1,0xF2,
            1,1,0x00, 
            0,1,0x26,
            1,1,0x01, 
            0,15,0xE0,
            1,1,0x0F, 
            1,1,0x1D, 
            1,1,0x1A, 
            1,1,0x0A, 
            1,1,0x0D, 
            1,1,0x07, 
            1,1,0x49, 
            1,1,0X66, 
            1,1,0x3B, 
            1,1,0x07, 
            1,1,0x11, 
            1,1,0x01, 
            1,1,0x09, 
            1,1,0x05, 
            1,1,0x04, 		 
            0,15,0XE1,
            1,1,0x00, 
            1,1,0x18, 
            1,1,0x1D, 
            1,1,0x02, 
            1,1,0x0F, 
            1,1,0x04, 
            1,1,0x36, 
            1,1,regval, 
            1,1,0x4C, 
            1,1,0x07, 
            1,1,0x13, 
            1,1,0x0F, 
            1,1,0x2E, 
            1,1,0x2F, 
            1,1,0x05, 
            0,4,0x2B, 
            1,1,0x00,
            1,1,0x00,
            1,1,0x01,
            1,1,0x3f,
            0,4,0x2A, 
            1,1,0x00,
            1,1,0x00,
            1,1,0x00,
            1,1,0xef,	 
            0,0,0x11,
            2, 0, 120,
            0,0,0x29,    
        )
        lcd_set_display_area = (
            0,4,0x2a,
            1,1,LCDPublic.XSTART_H,
            1,1,LCDPublic.XSTART_L,
            1,1,LCDPublic.XEND_H,
            1,1,LCDPublic.XEND_L,
            0,4,0x2b,
            1,1,LCDPublic.YSTART_H,
            1,1,LCDPublic.YSTART_L,
            1,1,LCDPublic.YEND_H,
            1,1,LCDPublic.YEND_L,
            0,0,0x2c,
        )
        lcd_display_on = (
            0, 0, 0x11,
            2, 0, 20,
            0, 0, 0x29,    
        )
        lcd_display_off = (
            0,0,0x28,
            2,0,120,
            0,0,0x10,    
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
    
    lcd_test = Ili9341()
    lcd_test.ShowAsciiStr(10, 10, 16, 24, 'QUECTEL',0xf800,0x001f)
