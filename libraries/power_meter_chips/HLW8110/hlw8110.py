from machine import UART
import utime

class Hlw8110(object):
    '''
    Hlw8110计量芯片类
    开放接口：read_i(),read_u(),read_power(),read_angle(),zx_en(),int_en(),process_int(),reset()
    '''

    # 计量寄存器地址 只读
    ANGLE_REG = 0X22  # 相角
    UFREG_REG = 0X23  # 电压频率
    RMSIA_REG = 0X24  # 通道 A 电流的有效值
    RMSU_REG = 0X26  # 电压有效值
    POWER_PA = 0X28  # 有功功率，默认读完清零
    POWER_S = 0X2E  # 视在功率
    EMU_STATE_REG = 0X2F  # 计量状态及校验和寄存器
    PEAK_IA = 0X30  # 电流A峰值，50Hz下，更新速率10s
    PEAK_U = 0X32  # 电压峰值，50Hz下，更新速率10s
    INSTAN_IA = 0X33  # 电流A瞬时值
    INSTAN_U = 0X35  # 电压瞬时值
    INSTAN_P = 0X3C  # 有功功率瞬时值
    INSTAN_S = 0X3D  # 视在功率瞬时值
    RMSIAC_REG = 0x70   # 电流有效值转换系数
    RMSUC_REG = 0x72  # 电压有效值转换系数
    POWER_PAC_REG = 0x73  # 有功功率有效值转换系数
    POWERSC_REG = 0x75  # 视在功率有效值转换系数

    # 中断寄存器
    IE_REG = 0X40  # 中断使能寄存器
    IF_REG = 0X41  # 中断状态寄存器，只读

    # 系统设置寄存器
    SYSCON_REG = 0X00  # 系统控制寄存器,默认0a04
    EMUCON_REG = 0X01  # 计量控制寄存器
    EMUCON2_REG = 0X13  # 计量控制寄存器2
    OVLVL_REG = 0X19  # 电压过压阈值设置
    OIALVL_REG = 0X1A  # 电流通道A过流阈值设置
    OIBLVL_REG = 0X1B  # 电流通道b过流阈值设置
    OPLVL_REG = 0X1C  # 有功功率过载阈值设置
    INT_REG = 0X1D  # 中断

    def __init__(self, child):
        self._child = child


    def reset(self):
        '''
        重置
        '''
        pass

    def read_i(self):
        '''
        读电流有效值寄存器和电流有效值转换系数，具体电流跟接入电路的电阻有关，本接口不做计算
        :return: 正常测量：(电流有效值寄存器值,电流有效值转换系数)
                 无有效数据：(0,0)
        '''
        #判断是交流电还是直流电
        cur_type = self._child.read_reg(self.EMUCON_REG)
        if len(cur_type) != 2:
            return (0,0)
        else:
            cur_type = cur_type[1] & (1<<5)

        # 读电流有效值转换系数
        ic_read = self._child.read_reg(self.RMSIAC_REG)  # 16位无符号数
        if len(ic_read) != 2:
            return (0,0)
        ic_data = (ic_read[0]<<8) +ic_read[1]

        #读电流有效值寄存器
        current_read = self._child.read_reg(self.RMSIA_REG)  # 24位有符号数
        if len(current_read) != 3:
            return (0,0)
        current_data = (current_read[0]<<16) + (current_read[1]<<8) + current_read[2]
        if cur_type:        #直流电
            #直流测量时，最高位为1，表示补码，计算有效值时，需要取绝对值
            if current_data & 0x800000:     #最高位为1，表示补码，计算有效值时，需要取绝对值
                current_data = ~(current_data & 0x7fffff - 1)
                return (current_data,ic_data)
            else:
                return (current_data,ic_data)
        else:               #交流电
            if current_data & 0x800000:     #最高位为1，表示数据为0
                return (0,ic_data)
            else:
                return (current_data,ic_data)

    def read_u(self):
        '''
        读电压有效值寄存器和电压有效值转换系数，本接口不做计算
        :return: 正常测量：(电压有效值寄存器值,电压有效值转换系数)
                 无有效数据：(0,0)
        '''
        # 判断是交流电还是直流电
        cur_type = self._child.read_reg(self.EMUCON_REG)
        if len(cur_type) != 2:
            return (0,0)
        else:
            cur_type = cur_type[1] & (1 << 4)
        # 读电压有效值转换系数
        uc_read = self._child.read_reg(self.RMSUC_REG)  # 16位无符号数
        if len(uc_read) != 2:
            return (0,0)
        uc_data = (uc_read[0] << 8) + uc_read[1]

        # 读电压有效值寄存器
        voltage_read = self._child.read_reg(self.RMSU_REG)  # 24位有符号数
        if len(voltage_read) != 3:
            return (0,0)
        voltage_data = (voltage_read[0] << 16) + (voltage_read[1] << 8) + voltage_read[2]
        if cur_type:  # 直流电
            # 直流测量时，最高位为1，表示补码，计算有效值时，需要取绝对值
            if voltage_data & 0x800000:  # 最高位为1，表示补码，计算有效值时，需要取绝对值
                voltage_data = ~(voltage_data & 0x7fffff - 1)
                return (voltage_data, uc_data)
            else:
                return (voltage_data, uc_data)
        else:  # 交流电
            if voltage_data & 0x800000:  # 最高位为1，表示数据为0
                return (0, uc_data)
            else:
                return (voltage_data, uc_data)

    def read_power(self):
        '''
        读有功功率寄存器和有功功率转换系数
        :return: 正常测量：(有功功率寄存器值,有功功率转换系数)
                 无有效数据：(0,0)
        '''
        # 读有功功率转换系数
        pc_read = self._child.read_reg(self.POWER_PAC_REG)  # 16位无符号数
        if len(pc_read) != 2:
            return (0,0)
        pc_read = (pc_read[0] << 8) + pc_read[1]

        # 读有功功率寄存器
        power_read = self._child.read_reg(self.POWER_PA)  # 32位有符号数
        if len(power_read) != 4:
            return (0,0)
        power_data = (power_read[0] << 24) + (power_read[1] << 16) + (power_read[2] << 8) + power_read[3]
        if power_data & 0x80000000:  # 补码，最高位是符号位
            power_data = ~(power_data & 0x7fffffff - 1)
            return (power_data, pc_read)
        else:
            return (power_data, pc_read)

    def read_angle(self):
        '''
        配置EMUCON2，然后读相角
        公式 1： 相角(50HZ) = Angle ∗ 0.0805,单位:度
        公式 2： 相角(60Hz) = Angle ∗ 0.0965，单位:度
        :return: 成功：相角
                 失败：-1
        '''
        #配置EMUCON2的必须配置ZXEN=1和WaveEn = 1
        conf_read = self._child.read_reg(self.EMUCON2_REG)
        if len(conf_read)<2:
            return -1
        conf_write = [conf_read[0], conf_read[1] | 0x24]
        self._child.write_reg(self.EMUCON2_REG,conf_write)
        #读相角寄存器值
        angle_read = self._child.read_reg(self.ANGLE_REG)
        if len(angle_read) != 2:
            return -1
        angle_read = (angle_read[0] << 8) +angle_read[1]
        #读取Ufreq(0x23)的值(16位无符号数)
        ufreq_read = self._child.read_reg(self.UFREG_REG)
        if len(ufreq_read) != 2:
            return -1
        ufreq_read = (ufreq_read[0] << 8) + ufreq_read[1]
        #计算线性频率
        f = 3579545 / (8 * ufreq_read)
        if abs(f - 50) <= 1:
            angle_data = angle_read * 0.0805
            return angle_data
        elif abs(f - 60) <= 1:
            angle_data = angle_read * 0.0965
            return angle_data
        else:
            return -1

    def zx_en(self,zx_type):
        '''
        过零检测使能
        @param zx_type: 过零输出方式
                        0：表示选择正向过零点作为过零检测信号，过零输出信号为信号频率/2
                        1：表示选择负向过零点作为过零检测信号，过零输出信号为信号频率/2
                        2,3：表示选择正向和负向过零点均作为过零检测信号，过零输出信号为信号频率
        :return: 成功：0
                 失败：-1
        '''
        #先使能zx
        conf_read = self._child.read_reg(self.EMUCON2_REG)
        if len(conf_read) != 2:
            return -1
        conf_write = [conf_read[0], conf_read[1] | 0x24]
        self._child.write_reg(self.EMUCON2_REG, conf_write)
        #再配置zx_type
        conf_read = self._child.read_reg(self.EMUCON_REG)
        if len(conf_read) != 2:
            return -1
        if zx_type in (0, 1):
            conf_write = [conf_read[0], conf_read[1] | (zx_type<<7)]
            self._child.write_reg(self.EMUCON_REG, conf_write)
        elif zx_type in (2, 3):
            conf_write = [conf_read[0] | 0x01, conf_read[1] | ((zx_type-2)<<7)]
            self._child.write_reg(self.EMUCON_REG, conf_write)
        return 0

    def int_en(self,int_type):
        '''
        中断使能
        int_type in range(16) 不为5, 且0,6,12,13,14,15bit默认开启，不受软件控制
        @param int_type: 中断类型
                        分别为：0：均值数据更新中断使能；1：PFA 中断使能；3：通道A有功电能寄存器溢出中断使能
                        6：瞬时中断使能；7：电流 A 过流中断使能；9：电压过压中断使能；10：功率过载的中断使能
                        11：电压欠压中断使能；13：电流 A过零中断使能；14：电压过零中断使能；15：漏电中断使能
        :return: 成功：0
                 失败：-1
        '''
        ie_read = self._child.read_reg(self.IE_REG)
        if len(ie_read) != 2:
            return -1
        if 0 <= int_type <= 7:
            ie_write = [ie_read[0], ie_read[1] | (1<<int_type)]
            self._child.write_reg(self.IE_REG, ie_write)
        elif int_type <= 15:
            ie_write = [ie_read[0] | (1<<(int_type-8)), ie_read[1]]
            self._child.write_reg(self.IE_REG, ie_write)
        else:
            return -1
        return 0

    def int_clear(self,int_type):
        '''
        清除中断使能
        0,6,12,13,14,15bit默认开启，不受软件控制
        @param int_type: 中断类型
                        分别为：0：均值数据更新中断使能；1：PFA 中断使能；3：通道A有功电能寄存器溢出中断使能
                        6：瞬时中断使能；7：电流 A 过流中断使能；9：电压过压中断使能；10：功率过载的中断使能
                        11：电压欠压中断使能；13：电流 A过零中断使能；14：电压过零中断使能；15：漏电中断使能
        :return: 成功：0
                 失败：-1
        '''
        ie_read = self._child.read_reg(self.IE_REG)
        if len(ie_read) != 2:
            return -1
        if 0 <= int_type <= 7:
            ie_write = [ie_read[0], ie_read[1] & ~(1 << int_type)]
            self._child.write_reg(self.IE_REG, ie_write)
        elif int_type <= 15:
            ie_write = [ie_read[0] & ~(1 << (int_type - 8)), ie_read[1]]
            self._child.write_reg(self.IE_REG, ie_write)
        else:
            return -1
        return 0

    def process_int(self):
        '''
        中断检测
        :return: 没有中断：0
                 有中断：中断号，可能包含多个中断
                 对应bit分别为：0：均值数据更新中断使能；1：PFA 中断使能；3：通道A有功电能寄存器溢出中断使能
                        6：瞬时中断使能；7：电流 A 过流中断使能；9：电压过压中断使能；10：功率过载的中断使能
                        11：电压欠压中断使能；13：电流 A过零中断使能；14：电压过零中断使能；15：漏电中断使能
        '''
        if_read = self._child.read_reg(self.IF_REG)
        if len(if_read) != 2:
            return 0
        in_flag = (if_read[0] << 8) + if_read[1]
        return in_flag

class Hlw8110_uart(Hlw8110):
    def __init__(self, uart_n, databits = 8, flowctl = 0):
        self.uart = UART(uart_n, 9600, databits, 1, 1, flowctl) #hlw8110固定9600波特率 偶校验even
        super().__init__(self)

    def read_reg(self,reg):
        '''
        读寄存器
        :param reg: 要读的寄存器
        :return: 成功：读出的数据
                 失败：空列表
        '''
        #发送读命令字节
        self.uart.write(bytearray([0xA5, reg]))
        check_data = 0xa5 + reg
        #uart判断是否有数据未读
        while 1:
            msglen = self.uart.any()
            if msglen:
                #读取数据
                r_data = list(self.uart.read(msglen))
                #校验数据
                for i in range(msglen-1):
                    check_data += r_data[i]
                check_data = ~check_data & 0xff
                if check_data == r_data[-1]:
                    return r_data[:-1]
                else:
                    return []

    def write_reg(self, reg, w_data):
        '''
        写寄存器
        :param cmd: 要写入的命令
        :param w_data: 要写入的数据，长度2的list或tuple
        :return: 0：成功
        '''
        cmd = reg | 0x80        #{1[bit7],REG_ADR[bit6:bit0]}
        #使能写操作0xA5 0xEA 0XE5 校验
        self.uart.write(bytearray([0xA5,0xEA,0xE5,0x8B]))
        #往寄存器写
        check_data = ~(0xA5 + cmd + w_data[0] + w_data[1]) & 0xff
        w_data = bytearray([0xA5, cmd, w_data[0], w_data[1],check_data])
        self.uart.write(w_data)
        #关闭写操作0xA5 0xEA 0XDC 校验
        self.uart.write(bytearray([0xA5, 0xEA, 0XDC, 0x94]))
        return 0

    def reset(self):
        '''
        复位指令0xA5 0xEA 0X96 校验
        '''
        self.uart.write(bytearray([0xA5, 0xEA, 0X96, 0xDA]))

if __name__ == '__main__':
    hlw8110 = Hlw8110_uart(uart_n=UART.UART2)
    # hlw8110.zx_en(zx_type=3)
    # hlw8110.int_en(int_type=0)
    hlw8110.int_en(int_type=11)     #电压欠压中断使能
    # hlw8110.int_clear(int_type=0)
    # hlw8110.int_clear(int_type=11)
    print('IE_reg value is set to {}'.format(hlw8110.read_reg(hlw8110.IE_REG)))
    for i in range(2):
        print("start reading...")
        curr,ic = hlw8110.read_i()
        volt,uc = hlw8110.read_u()
        power,pc = hlw8110.read_power()
        angle = hlw8110.read_angle()
        print("reading complete.")
        #根据外部电路计算电流，电压，有功功率
        if curr:
            print("电流寄存器值：{0}, 电流有效值转换系数：{1}".format(curr, ic))
        if volt:
            print("电压寄存器值：{0}, 电压有效值转换系数：{1}".format(volt, uc))
        if power:
            print("有功功率寄存器值：{0}, 有功功率转换系数：{1}".format(power,pc))
        if angle != -1:
            print("相角：{}".format(angle))
        utime.sleep(1)
        while True:
            flag = hlw8110.process_int() #注意，0,6,12,13,14,15位无论使能与否，都会产生中断
            if (flag & 0x0800):
                print('电压欠压中断 just happened')
                break
            utime.sleep_ms(100)

