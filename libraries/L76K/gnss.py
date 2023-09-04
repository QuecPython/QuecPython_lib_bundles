from gnss import GnssGetData
import utime

class Gnss(object):
    def __init__(self,uartn,baudrate,databits,parity,stopbits,flowctl):
        self._gnss = GnssGetData(uartn, baudrate, databits, parity, stopbits, flowctl)

    def read_gnss(self,retry = 1,debug = 0):
        '''
        读取GNSS数据
        :param retry: 重试次数
        :param debug: 输出调试信息
        :return: -1 失败
                (有效位，原始GNSS数据) 成功
                 有效位(0x01-0x07)：  0x04 gga有效
                                    0x02 rmc有效
                                    0x01 gsv有效，
        '''
        self._gnss.read_gnss_data(retry,debug)
        gga_valid, rmc_valid, gsv_valid = self._gnss.checkDataValidity()
        data = self._gnss.getOriginalData()
        data_valid = 0x00
        if not (gga_valid | rmc_valid | gsv_valid):
            return -1
        if gga_valid:
            data_valid |= 0x04
        if rmc_valid:
            data_valid |= 0x02
        if gsv_valid:
            data_valid |= 0x01
        return (data_valid,data)

    def isFix(self):
        '''
        检查是否定位成功
        :return:1：定位成功 0:失败
        '''
        return self._gnss.isFix()

    def getUtcTime(self):
        '''
        获取定位的UTC时间
        :return:成功返回UTC时间，字符串类型，失败返回整型-1。
        '''
        return self._gnss.getUtcTime()

    def getLocationMode(self):
        '''
        获取GPS模块定位模式
        :return: -1	获取失败，串口未读到数据或未读到有效数据
                  0	定位不可用或者无效
                  1	定位有效,定位模式：GPS、SPS 模式
                  2	定位有效,定位模式： DGPS、DSPS 模式
                  6	估算（航位推算）模式
        '''
        return self._gnss.getLocationMode()

    def getUsedSateCnt(self):
        '''
        获取GPS模块定位使用卫星数量
        :return:成功返回GPS模块定位使用卫星数量，返回值类型为整型，失败返回整型-1。
        '''
        return self._gnss.getUsedSateCnt()

    def getLocation(self):
        '''
        获取GPS模块定位的经纬度信息
        :return:成功返回GPS模块定位的经纬度信息，失败返回整型-1；成功时返回值格式如下：
                (longitude, lon_direction, latitude, lat_direction)
                longitude - 经度，float型
                lon_direction - 经度方向，字符串类型，E表示东经，W表示西经
                latitude - 纬度，float型
                lat_direction - 纬度方向，字符串类型，N表示北纬，S表示南纬
        '''
        return self._gnss.getLocation()

    def getViewedSateCnt(self):
        '''
        获取GPS模块定位可见卫星数量
        :return:成功返回GPS模块定位可见卫星数量，整型值，失败返回整型-1。
        '''
        return self._gnss.getViewedSateCnt()

    def getGeodeticHeight(self):
        '''
        获取GPS模块定位海拔高度
        :return:成功返回浮点类型海拔高度(单位:米)，失败返回整型-1。
        '''
        return self._gnss.getGeodeticHeight()

    def getCourse(self):
        '''
        获取可视的GNSS卫星方位角
        :return:返回所有可视的GNSS卫星方位角，范围：0 ~ 359，以正北为参考平面。
                返回形式为字典，其中key表示卫星编号，value表示方位角。
                要注意，value的值可能是一个整型值，也可能是''，这取决于原始的GNSS数据中GPGSV语句中方位角是否有值。
        '''
        return self._gnss.getCourse()

    def getSpeed(self):
        '''
        获取GPS模块对地速度
        :return:成功返回GPS模块对地速度(单位:KM/h)，浮点类型，失败返回整型-1
        '''
        return self._gnss.getSpeed()

if __name__ == "__main__":
    gnss = Gnss(1, 9600, 8, 0, 1, 0)
    for i in range(10):
        print("开始读取GNSS数据")
        print(gnss.read_gnss(retry=3))
        utime.sleep(1)
        print("定位是否成功 {}".format(gnss.isFix()))
        print("定位时间 {}".format(gnss.getUtcTime()))
        print("GPS定位模式 {}".format(gnss.getLocationMode()))
        print("GPS使用卫星数量 {}".format(gnss.getUsedSateCnt()))
        print("GPS位置 {}".format(gnss.getLocation()))
        print("GPS模块定位可见卫星数量 {}".format(gnss.getViewedSateCnt()))
        print("GPS模块定位海拔高度 {}".format(gnss.getGeodeticHeight()))
        print("获取可视的GNSS卫星方位角 {}".format(gnss.getCourse()))
        print("获取GPS模块对地速度 {}".format(gnss.getSpeed()))
        utime.sleep(1)
