
# import RPi.GPIO as GPIO
# import spidev
# import signal
# import time
# import logging
# https://github.com/pimylifeup/Mfrc522-python/blob/master/Mfrc522/Mfrc522.py

from machine import Pin
from machine import SPI
import utime
from machine import ExtInt
import _thread


class Mfrc522(object):
    '''
    RC522类
    开放接口：write(text)，read()，read_id(),Mfrc522_Read(blockAddr),Mfrc522_Write(blockAddr, writeData)
    '''
    MAX_LEN = 16

    PCD_IDLE = 0x00         #取消当前命令
    PCD_AUTHENT = 0x0E      #验证密钥
    PCD_RECEIVE = 0x08      #接收数据
    PCD_TRANSMIT = 0x04     #发送消息
    PCD_TRANSCEIVE = 0x0C   #发送并接收数据
    PCD_RESETPHASE = 0x0F   #复位
    PCD_CALCCRC = 0x03      #CRC计算

    PICC_REQIDL = 0x26      #寻天线区内未进入休眠状态的卡
    PICC_REQALL = 0x52      #寻天线区内全部卡
    PICC_ANTICOLL = 0x93    #防冲撞
    #修改点，之前93重复
    PICC_SElECTTAG = 0x95   #寻卡
    PICC_AUTHENT1A = 0x60   #验证A密钥
    PICC_AUTHENT1B = 0x61   #验证B密钥
    PICC_READ = 0x30        #读块
    PICC_WRITE = 0xA0       #写块
    PICC_DECREMENT = 0xC0   #扣款
    PICC_INCREMENT = 0xC1   #充值
    PICC_RESTORE = 0xC2     #调块数据到缓冲区
    PICC_TRANSFER = 0xB0    #保存缓冲区数据
    PICC_HALT = 0x50        #休眠

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    #寄存器
    Reserved00 = 0x00
    CommandReg = 0x01
    CommIEnReg = 0x02
    DivlEnReg = 0x03
    CommIrqReg = 0x04
    DivIrqReg = 0x05
    ErrorReg = 0x06
    Status1Reg = 0x07
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    WaterLevelReg = 0x0B
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    CollReg = 0x0E
    Reserved01 = 0x0F

    Reserved10 = 0x10
    ModeReg = 0x11
    TxModeReg = 0x12
    RxModeReg = 0x13
    TxControlReg = 0x14
    TxAutoReg = 0x15
    TxSelReg = 0x16
    RxSelReg = 0x17
    RxThresholdReg = 0x18
    DemodReg = 0x19
    Reserved11 = 0x1A
    Reserved12 = 0x1B
    MifareReg = 0x1C
    Reserved13 = 0x1D
    Reserved14 = 0x1E
    SerialSpeedReg = 0x1F

    Reserved20 = 0x20
    CRCResultRegM = 0x21
    CRCResultRegL = 0x22
    Reserved21 = 0x23
    ModWidthReg = 0x24
    Reserved22 = 0x25
    RFCfgReg = 0x26
    GsNReg = 0x27
    CWGsPReg = 0x28
    ModGsPReg = 0x29
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    Reserved30 = 0x30
    TestSel1Reg = 0x31
    TestSel2Reg = 0x32
    TestPinEnReg = 0x33
    TestPinValueReg = 0x34
    TestBusReg = 0x35
    AutoTestReg = 0x36
    VersionReg = 0x37
    AnalogTestReg = 0x38
    TestDAC1Reg = 0x39
    TestDAC2Reg = 0x3A
    TestADCReg = 0x3B
    Reserved31 = 0x3C
    Reserved32 = 0x3D
    Reserved33 = 0x3E
    Reserved34 = 0x3F

    serNum = []
    KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    BLOCK_ADDRS = [8, 9, 10]

    def __init__(self):

        self.Mfrc522_Init()


    def _Mfrc522_Reset(self):
        self._Write_Mfrc522(self.CommandReg, self.PCD_RESETPHASE)

    def _Write_Mfrc522(self, addr, val):
        print("this bug write")
        raise NotImplementedError

    def _Read_Mfrc522(self, addr):
        print("this bug read")
        raise NotImplementedError

    def _Close_Mfrc522(self):
        raise NotImplementedError

    def _SetBitMask(self, reg, mask):
        tmp = self._Read_Mfrc522(reg)
        self._Write_Mfrc522(reg, tmp | mask)

    def _ClearBitMask(self, reg, mask):
        '''
        寄存器清位
        '''
        tmp = self._Read_Mfrc522(reg)
        self._Write_Mfrc522(reg, tmp & (~mask))

    def AntennaOn(self):
        '''
        开启天线
        '''
        temp = self._Read_Mfrc522(self.TxControlReg)
        if (~(temp & 0x03)):
            self._SetBitMask(self.TxControlReg, 0x03)

    def AntennaOff(self):
        '''
        关闭天线
        '''
        self._ClearBitMask(self.TxControlReg, 0x03)

    def _Mfrc522_ToCard(self, command, sendData):
        backData = []
        backLen = 0
        status = self.MI_ERR
        irqEn = 0x00
        waitIRq = 0x00
        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIRq = 0x10
        if command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIRq = 0x30

        self._Write_Mfrc522(self.CommIEnReg, irqEn | 0x80)
        self._ClearBitMask(self.CommIrqReg, 0x80)
        self._SetBitMask(self.FIFOLevelReg, 0x80)

        self._Write_Mfrc522(self.CommandReg, self.PCD_IDLE)

        for i in range(len(sendData)):
            self._Write_Mfrc522(self.FIFODataReg, sendData[i])

        self._Write_Mfrc522(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self._SetBitMask(self.BitFramingReg, 0x80)

        i = 5
        while True:
            n = self._Read_Mfrc522(self.CommIrqReg)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & waitIRq)):
                break

        self._ClearBitMask(self.BitFramingReg, 0x80)

        if i != 0:
            if (self._Read_Mfrc522(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK
                if n & irqEn & 0x01:
                    status = self.MI_NOTAGERR
                if command == self.PCD_TRANSCEIVE:
                    n = self._Read_Mfrc522(self.FIFOLevelReg)
                    lastBits = self._Read_Mfrc522(self.ControlReg) & 0x07
                    if lastBits != 0:
                        backLen = (n - 1) * 8 + lastBits
                    else:
                        backLen = n * 8

                    if n == 0:
                        n = 1
                    if n > self.MAX_LEN:
                        n = self.MAX_LEN

                    for i in range(n):
                        backData.append(self._Read_Mfrc522(self.FIFODataReg))
            else:
                status = self.MI_ERR

        return (status, backData, backLen)

    def _Mfrc522_Request(self, reqMode):
        '''
        寻卡
        '''
        TagType = []

        self._Write_Mfrc522(self.BitFramingReg, 0x07)

        TagType.append(reqMode)
        (status, backData, backBits) = self._Mfrc522_ToCard(
            self.PCD_TRANSCEIVE, TagType)

        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR

        return (status, backBits)

    def _Mfrc522_Anticoll(self):
        '''
        防冲撞
        '''
        serNumCheck = 0

        serNum = []

        self._Write_Mfrc522(self.BitFramingReg, 0x00)

        serNum.append(self.PICC_ANTICOLL)
        serNum.append(0x20)

        (status, backData, backBits) = self._Mfrc522_ToCard(
            self.PCD_TRANSCEIVE, serNum)

        if (status == self.MI_OK):
            i = 0
            if len(backData) == 5:
                for i in range(4):
                    serNumCheck = serNumCheck ^ backData[i]
                if serNumCheck != backData[4]:
                    status = self.MI_ERR
            else:
                status = self.MI_ERR

        return (status, backData)

    def _CalulateCRC(self, pIndata):
        self._ClearBitMask(self.DivIrqReg, 0x04)
        self._SetBitMask(self.FIFOLevelReg, 0x80)

        for i in range(len(pIndata)):
            self._Write_Mfrc522(self.FIFODataReg, pIndata[i])

        self._Write_Mfrc522(self.CommandReg, self.PCD_CALCCRC)
        i = 0xFF
        while True:
            n = self._Read_Mfrc522(self.DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        pOutData = []
        pOutData.append(self._Read_Mfrc522(self.CRCResultRegL))
        pOutData.append(self._Read_Mfrc522(self.CRCResultRegM))
        return pOutData

    def _Mfrc522_SelectTag(self, serNum):
        '''
        选择卡片
        '''
        backData = []
        buf = []
        buf.append(self.PICC_SElECTTAG)
        buf.append(0x70)

        for i in range(5):
            buf.append(serNum[i])

        pOut = self._CalulateCRC(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self._Mfrc522_ToCard(
            self.PCD_TRANSCEIVE, buf)

        if (status == self.MI_OK) and (backLen == 0x18):
            print("Size: " + str(backData[0]))
            return backData[0]
        else:
            return 0

    def Mfrc522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
        '''
        验证卡片密码
        '''
        buff = []

        # First byte should be the authMode (A or B)
        buff.append(authMode)

        # Second byte is the trailerBlock (usually 7)
        buff.append(BlockAddr)

        # Now we need to append the authKey which usually is 6 bytes of 0xFF
        for i in range(len(Sectorkey)):
            buff.append(Sectorkey[i])

        # Next we append the first 4 bytes of the UID
        for i in range(4):
            buff.append(serNum[i])

        # Now we start the authentication itself
        (status, backData, backLen) = self._Mfrc522_ToCard(self.PCD_AUTHENT, buff)

        # Check if an error occurred
        if not (status == self.MI_OK):
            print("AUTH ERROR!!")
        if not (self._Read_Mfrc522(self.Status2Reg) & 0x08) != 0:
            print("AUTH ERROR(status2reg & 0x08) != 0")

        # Return the status
        return status

    def Mfrc522_StopCrypto1(self):
        self._ClearBitMask(self.Status2Reg, 0x08)

    def Mfrc522_Read(self, blockAddr):
        '''
        读数据
        '''
        recvData = []
        recvData.append(self.PICC_READ)
        recvData.append(blockAddr)
        pOut = self._CalulateCRC(recvData)
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        (status, backData, backLen) = self._Mfrc522_ToCard(
            self.PCD_TRANSCEIVE, recvData)
        if not (status == self.MI_OK):
            print("Error while reading!")

        if len(backData) == 16:
            print("Sector " + str(blockAddr) + " " + str(backData))
            return backData
        else:
            return None

    def Mfrc522_Write(self, blockAddr, writeData):
        '''
        写数据到卡
        @param blockAddr: 块地址
        @param writeData: 写入的数据，16字节
        '''
        buff = []
        buff.append(self.PICC_WRITE)
        buff.append(blockAddr)
        crc = self._CalulateCRC(buff)
        buff.append(crc[0])
        buff.append(crc[1])
        (status, backData, backLen) = self._Mfrc522_ToCard(
            self.PCD_TRANSCEIVE, buff)
        if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR

        print("%s backdata &0x0F == 0x0A %s" % (backLen, backData[0] & 0x0F))
        if status == self.MI_OK:
            buf = []
            for i in range(16):
                buf.append(writeData[i])

            crc = self._CalulateCRC(buf)
            buf.append(crc[0])
            buf.append(crc[1])
            (status, backData, backLen) = self._Mfrc522_ToCard(
                self.PCD_TRANSCEIVE, buf)
            if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
                print("Error while writing")
            if status == self.MI_OK:
                print("Data written")

    def Mfrc522_DumpClassic1K(self, key, uid):
        for i in range(64):
            status = self.Mfrc522_Auth(self.PICC_AUTHENT1A, i, key, uid)
            # Check if authenticated
            if status == self.MI_OK:
                self.Mfrc522_Read(i)
            else:
                print("Authentication error")

    def Mfrc522_Init(self):
        self._Mfrc522_Reset()

        self._Write_Mfrc522(self.TModeReg, 0x8D)
        self._Write_Mfrc522(self.TPrescalerReg, 0x3E)
        self._Write_Mfrc522(self.TReloadRegL, 30)
        self._Write_Mfrc522(self.TReloadRegH, 0)

        self._Write_Mfrc522(self.TxAutoReg, 0x40)
        self._Write_Mfrc522(self.ModeReg, 0x3D)
        self.AntennaOff()
        self.AntennaOn()
        self.M500PcdConfigISOType('A')

    def M500PcdConfigISOType(self, type):

        if type == 'A':
            self._ClearBitMask(self.Status2Reg, 0x08)
            self._Write_Mfrc522(self.ModeReg, 0x3D)
            self._Write_Mfrc522(self.RxSelReg, 0x86)
            self._Write_Mfrc522(self.RFCfgReg, 0x7F)
            self._Write_Mfrc522(self.TReloadRegL, 30)
            self._Write_Mfrc522(self.TReloadRegH, 0)
            self._Write_Mfrc522(self.TModeReg, 0x8D)
            self._Write_Mfrc522(self.TPrescalerReg, 0x3E)
            utime.sleep_us(1000)
            self.AntennaOn()
        else:
            return 1

    def read(self):
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
        return id, text

    def read_id(self):
        '''
        读id
        '''
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        (status, TagType) = self._Mfrc522_Request(self.PICC_REQIDL)
        if status != self.MI_OK:
            return None
        (status, uid) = self._Mfrc522_Anticoll()
        if status != self.MI_OK:
            return None
        print("uid=", uid)
        return self._uid_to_num(uid)

    def read_no_block(self):
        (status, TagType) = self._Mfrc522_Request(self.PICC_REQIDL)
        if status != self.MI_OK:
            return None, None
        (status, uid) = self._Mfrc522_Anticoll()
        if status != self.MI_OK:
            return None, None
        id = self._uid_to_num(uid)
        self._Mfrc522_SelectTag(uid)
        status = self.Mfrc522_Auth(
            self.PICC_AUTHENT1A, 11, self.KEY, uid)
        data = []
        text_read = ''
        if status == self.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                block = self.Mfrc522_Read(block_num)
                if block:
                    data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
        self.Mfrc522_StopCrypto1()
        return id, text_read

    def write(self, text):
        id, text_in = self.write_no_block(text)
        while not id:
            id, text_in = self.write_no_block(text)
        return id, text_in

    def write_no_block(self, text):
        (status, TagType) = self._Mfrc522_Request(self.PICC_REQIDL)
        if status != self.MI_OK:
            print("cannot find the card!")
            return None, None
        (status, uid) = self._Mfrc522_Anticoll()
        if status != self.MI_OK:
            return None, None
        id = self._uid_to_num(uid)
        self._Mfrc522_SelectTag(uid)
        status = self.Mfrc522_Auth(
            self.PICC_AUTHENT1A, 11, self.KEY, uid)
        self.Mfrc522_Read(11)
        if status == self.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(
                len(self.BLOCK_ADDRS) * 16).encode('ascii')))
            i = 0
            for block_num in self.BLOCK_ADDRS:
                self.Mfrc522_Write(block_num, data[(i*16):(i+1)*16])
                i += 1
        self.Mfrc522_StopCrypto1()
        return id, text[0:(len(self.BLOCK_ADDRS) * 16)]

    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

    def _irq_callback(self, para):
        print("irq call:", para)
        self.read_id_no_block()

    def _irq_set(self, pin_irq, irq_cb):
        if pin_irq is None:
            print("Interrupt pin is not set")
            return

        regVal = 0
        # self._Write_Mfrc522(self.CommIEnReg, regVal)
        self._Write_Mfrc522(self.CommIEnReg, regVal | 0x20)
        self._Write_Mfrc522(self.DivlEnReg, 0x90)

        print("get enreg:",self._Read_Mfrc522(self.CommIEnReg))

        if irq_cb is None:
            self._irq_fun = self._irq_callback
        else:
            self._irq_fun = irq_cb

        print("p_irq = ",pin_irq)
        self._irq = ExtInt(pin_irq, ExtInt.IRQ_FALLING,
                           ExtInt.PULL_PU, self._irq_fun)


class Mfrc522_spi(Mfrc522):

    def __init__(self, spi=None, *, spi_no=1, spi_mode=0, spi_clk=0, pin_rst, pin_irq=None, irq_cb=None):
        if spi is None:
            self._spi = SPI(spi_no, spi_mode, spi_clk)
        else:
            self._spi = spi
        self._rst = Pin(pin_rst, Pin.OUT, Pin.PULL_DISABLE, 0)
        utime.sleep(1)
        self._rst.write(1)
        if pin_irq != None:
            self._irq_set(pin_irq, irq_cb)

        super().__init__()

    def _Write_Mfrc522(self, addr, val):
        write_buf = bytearray([(addr << 1) & 0x7E, val])
        # print("write_buf:",write_buf)
        self._spi.write(write_buf, len(write_buf))

    def _Read_Mfrc522(self, addr):
        write_buf = bytearray([((addr << 1) & 0x7E) | 0x80, 0])
        read_buf = bytearray(len(write_buf))
        self._spi.write_read(read_buf, write_buf, len(write_buf))
        # print("read_buf:",read_buf)
        return read_buf[1]

    def _Close_Mfrc522(self):
        pass

def rc522_test():
    reader = Mfrc522_spi(pin_rst=Pin.GPIO12, pin_irq=Pin.GPIO11)
    print("init finish.")
    blockAddr = 0x01
    data = [0x00,0x0A,0x10,0x00,0x0C,0x00,0xA0,0x05,0x00,0x40,0x40,0x00,0x10,0x20]
    reader.Mfrc522_Write(blockAddr,data)
    read_data = reader.Mfrc522_Read(blockAddr)
    #id = reader.read_id()
    print('card id is {0}'.format(read_data))
    utime.sleep_ms(200)

if __name__ == '__main__':
    _thread.start_new_thread(rc522_test, ())
