from usr import LCDPublic

class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


class Peripheral_LCD(object):
    '''
    LCD通用类,定义LCD屏的通用行为
    开放接口：
    DrawPoint(x, y, color),DrawLine(x0, y0, x1, y1, color),DrawRectangle(x0, y0, x1, y1, color)
    Clear(color),DrawCircle(x0, y0, r, color),ShowChar(x, y, xsize, ysize, ch_buf, fc, bc)
    ShowAscii(x, y, xsize, ysize, ch, fc, bc),ShowAsciiStr(x, y, xsize, ysize, str_ascii, fc, bc)
    ShowJpg(name, start_x, start_y), lcd_show_chinese(x, y, xsize, ysize, ch, fc, bc),
    lcd_show_chinese_str(x, y, xsize, ysize, str_ch, fc, bc),lcd_show_image(image_data, x, y, width, heigth)
    lcd_show_image_file(path, x, y, width, heigth, h)
    '''
    def __init__(self, child_self=None):

        if child_self is None:
            raise CustomError("child LCD should be init first. ")
        else:
            self._child_self = child_self

    def DrawPoint(self, x, y, color):
        '''
        画点
        :param x: x
        :param y: y
        :param color: color
        '''
        tmp = color.to_bytes(2, 'little')
        self._child_self._lcd.lcd_write(bytearray(tmp), x, y, x, y)


    def Clear(self, color):
        '''
        清屏
        :param color: color
        '''
        self._child_self._lcd.lcd_clear(color)

    def Fill(self, x_s, y_s, x_e, y_e, color):
        '''
        填充以起始坐标和结束坐标为对角线的矩形
        :param x_s: 起始x坐标
        :param y_s: 起始y坐标
        :param x_e: 结束x坐标
        :param y_e: 结束y坐标
        :param color: color
        '''
        tmp = color.to_bytes(2, 'little')
        count = (x_e - x_s + 1)*(y_e - y_s + 1)

        color_buf = bytearray(0)

        for i in range(count):
            color_buf += tmp

        self._child_self._lcd.lcd_write(color_buf, x_s, y_s, x_e, y_e)

    def ColorFill(self, x_s, y_s, x_e, y_e, color_buff):
        self._child_self._lcd.lcd_write(color_buff, x_s, y_s, x_e, y_e)

    def DrawLine(self, x0, y0, x1, y1, color):
        '''
        画线
        '''
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        if y0 < y1:
            ystep = 1
        else:
            ystep = -1
        while x0 <= x1:
            if steep:
                self.DrawPoint(y0, x0, color)
            else:
                self.DrawPoint(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def DrawRectangle(self, x0, y0, x1, y1, color):
        '''
        画矩形
        '''
        self.DrawLine(x0,y0,x1,y0,color)
        self.DrawLine(x0,y0,x0,y1,color)
        self.DrawLine(x0,y1,x1,y1,color)
        self.DrawLine(x1,y0,x1,y1,color)

    def DrawCircle(self, x0, y0, r, color):
        '''
        画圆
        '''
        a = 0
        b = r
        di = 3 - (r << 1)

        while a <= b:
            self.DrawPoint(x0+a,y0-b,color)
            self.DrawPoint(x0+b,y0-a,color)    
            self.DrawPoint(x0+b,y0+a,color)            
            self.DrawPoint(x0+a,y0+b,color)
            self.DrawPoint(x0-a,y0+b,color)
            self.DrawPoint(x0-b,y0+a,color)
            self.DrawPoint(x0-a,y0-b,color)
            self.DrawPoint(x0-b,y0-a,color)
            a += 1
            if(di < 0):
                di += 4*a+6
            else:
                di += 10+4*(a-b) 
                b -= 1

    def ShowChar(self, x, y, xsize, ysize, ch_buf, fc, bc):
        '''
        单个字符显示，包括汉字和ASCII
        :param x:x轴坐标
        :param y:y轴坐标
        :param xsize:字体宽度
        :param ysize:字体高度
        :param ch_buf:存放汉字字模的元组或者列表
        :param fc:字体颜色，RGB565
        :param bc:背景颜色，RGB565
        '''
        rgb_buf = []
        t1 = xsize // 8
        t2 = xsize % 8
        if t2 != 0:
            xsize = (t1 + 1) * 8
        for i in range(0, len(ch_buf)):
            for j in range(0, 8):
                if (ch_buf[i] << j) & 0x80 == 0x00:
                    rgb_buf.append(bc & 0xff)
                    rgb_buf.append(bc >> 8)
                else:
                    rgb_buf.append(fc & 0xff)
                    rgb_buf.append(fc >> 8)
        self._child_self._lcd.lcd_write(bytearray(rgb_buf), x, y, x + xsize - 1, y + ysize - 1)

    def ShowAscii(self, x, y, xsize, ysize, ch, fc, bc):
        '''
        ASCII字符显示,目前支持8x16、16x24的字体大小
        :param x:x轴显示起点
        :param y:y轴显示起点
        :param xsize:字体宽度
        :param ysize:字体高度
        :param ch:待显示的ASCII字符
        :param fc:字体颜色，RGB565
        :param bc:背景颜色，RGB565
        '''
        ascii_dict = {}
        if xsize == 8 and ysize == 16:
            ascii_dict = LCDPublic.ascii_8x16_dict
        elif xsize == 16 and ysize == 24:
            ascii_dict = LCDPublic.ascii_16x24_dict

        for key in ascii_dict:
            if ch == key:
                self.ShowChar(x, y, xsize, ysize, ascii_dict[key], fc, bc)


    def ShowAsciiStr(self, x, y, xsize, ysize, str_ascii, fc, bc):
        '''
        ASCII字符串显示
        :param x:x轴显示起点
        :param y:y轴显示起点
        :param xsize:字体宽度
        :param ysize:字体高度
        :param str_ascii:待显示的ASCII字符串
        :param fc:字体颜色，RGB565
        :param bc:背景颜色，RGB565
        '''
        xs = x
        ys = y
        if (len(str_ascii) * xsize + x) > self._child_self._lcd_w:
            raise Exception('Display out of range')
        for ch in str_ascii:
            self.ShowAscii(xs, ys, xsize, ysize, ch, fc, bc)
            xs += xsize

    def ShowJpg(self,name, start_x, start_y):
        '''
        显示图片
        :param name: 图片名
        :param start_x: start_x
        :param start_y: start_
        '''
        self._child_self._lcd.lcd_show_jpg(name, start_x, start_y)

    def lcd_show_chinese(self, x, y, xsize, ysize, ch, fc, bc):
        '''
        汉字显示,目前支持16x16、16x24、24x24的字体大小
        :param x:x轴显示起点
        :param y:y轴显示起点
        :param xsize:字体宽度
        :param ysize:字体高度
        :param ch:待显示的汉字
        :param fc:字体颜色，RGB565
        :param bc:背景颜色，RGB565
        '''
        hanzi_dict = {}
        if xsize == 16 and ysize == 16:
            hanzi_dict = LCDPublic.hanzi_16x16_dict
        elif xsize == 16 and ysize == 24:
            hanzi_dict = LCDPublic.hanzi_16x24_dict
        elif xsize == 24 and ysize == 24:
            hanzi_dict = LCDPublic.hanzi_24x24_dict

        for key in hanzi_dict:
            if ch == key:
                self.ShowChar(x, y, xsize, ysize, hanzi_dict[key], fc, bc)

    def lcd_show_chinese_str(self, x, y, xsize, ysize, str_ch, fc, bc):
        '''
        汉字字符串显示
        :param x:x轴显示起点
        :param y:y轴显示起点
        :param xsize:字体宽度
        :param ysize:字体高度
        :param str_ch:待显示的汉字字符串
        :param fc:字体颜色，RGB565
        :param bc:背景颜色，RGB565
        '''
        xs = x
        ys = y
        # print('chstrlen={}, w={}'.format(len(str), self.lcd_w))
        if (len(str_ch) / 3 * xsize + x) > self._child_self._lcd_w:
            raise Exception('Display out of range')
        for i in range(0, len(str_ch), 3):
            index = i + 3
            ch = str_ch[i:index]
            self.lcd_show_chinese(xs, ys, xsize, ysize, ch, fc, bc)
            xs += xsize

    def lcd_show_image(self, image_data, x, y, width, heigth):
        '''
        bytearray图片显示，如果图片宽高小于80x80，可直接该函数一次性写入并显示
        :param image_data:存放待显示图片的RGB数据
        :param x:起点x
        :param y:起点y
        :param width:图片宽度
        :param heigth:图片高度
        '''
        self._child_self._lcd.lcd_write(bytearray(image_data), x, y, x + width - 1, y + heigth - 1)

    def lcd_show_image_file(self, path, x, y, width, heigth, h):
        '''
        图片显示，如果图片宽高大于80x80，用该函数来分段写入显示，分段写入原理如下：
        以要显示图片的宽度为固定值，将待显示的图片分成若干宽高为 width * h 大小的图片，最后一块高度不足h的按实际高度计算，
        h为分割后每个图片的高度，可由用户通过参数 h 指定，h的值应该满足关系： width * h * 2 < 4096
        :param path:存放图片数据的txt文件路径，包含文件名，如 '/usr/image.txt.py'
        :param x:起点x
        :param y:起点y
        :param width:图片宽度
        :param heigth:图片高度
        :param h:分割后每个图片的高度
        '''
        image_data = []
        read_n = 0  # 已经读取的字节数
        byte_n = 0  # 字节数
        xs = x
        ys = y
        h_step = h  # 按高度h_step个像素点作为步长
        h1 = heigth // h_step  # 当前图片按h_step大小分割，可以得到几个 width * h_step 大小的图片
        h2 = heigth % h_step  # 最后剩下的一块 大小不足 width * h_step 的图片的实际高度
        with open(path, "r", encoding='utf-8') as fd:
            end = ''
            while not end:
                line = fd.readline()
                if line == '':
                    end = 1
                else:
                    curline = line.strip('\r\n').strip(',').split(',')
                    for i in curline:
                        byte_n += 1
                        read_n += 1
                        image_data.append(int(i))
                        if h1 > 0 and byte_n == width * h_step * 2:
                            self.lcd_show_image(image_data, xs, ys, width, h_step)
                            image_data = []
                            ys = ys + h_step
                            h1 -= 1
                            byte_n = 0
                            # print('image_data len = {}'.format(len(image_data)))
                        elif h1 == 0 and read_n == width * heigth * 2:
                            if h2 != 0:
                                self.lcd_show_image(image_data, xs, ys, width, h2)

    @staticmethod
    def get_rgb565_color(r, g, b):
        '''
        将24位色转换位16位色
        如红色的24位色为0xFF0000，则r=0xFF,g=0x00,b=0x00,
        将r、g、b的值传入下面函数即可得到16位相同颜色数据
        '''
        return ((r << 8) & 0xF800) | ((g << 3) & 0x07E0) | ((b >> 3) & 0x001F)


    


         
