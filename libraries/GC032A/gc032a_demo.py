from usr.st7789 import LCD_ST7789
from usr import CommonCamera
import utime as time

def cap_callback(LCD):
    LCD.Clear(0xFFFF)
    time.sleep(2)
    LCD._lcd.lcd_show_jpg('/usr/pic_01.jpeg', 0, 0)

if __name__ == '__main__':
    new_lcd = LCD_ST7789()
    print("lcd init. ")
    my_gc032a = CommonCamera(0,capt_callback=cap_callback)
    my_gc032a.cap_open()
    time.sleep(1)
    my_gc032a.start(name="pic_01")

