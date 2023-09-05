import slip
import dataCall
import utime
import usocket
import checkNet
from machine import UART
from usr.common_except import CustomError

class Esp8266(object):
	def __init__(self):
		self._wait_datacall_success()

	def _wait_datacall_success(self):
		print('waiting datacall success...')
		while 1:
			self.lteInfo = dataCall.getInfo(1, 0)
			if self.lteInfo != -1:
				break
			utime.sleep(2)
		print('success get dataCall info: ')
		print(self.lteInfo)

class Esp8266_ap(Esp8266):
	ESP_SERVER = '172.16.1.5'
	ESP_SERVER_PORT = 1000

	def __init__(self,uart):
		super().__init__()
		self.wifi_off()
		# 创建slip网卡
		ret = slip.construct(uart, slip.SLIP_INNER, 0)
		print(ret)
		if ret != 0:
			raise CustomError("slip netif construct fail")

	def _pack_tlv_format(self,head, content):
		if len(content) == 0 or len(content) > 9999 or len(head) != 2:
			print('illegal tlv content')
			return 0
		len_str = '%04d' % len(content)
		msg = head + len_str + content
		return msg

	def wifi_on(self):
		# 获取slip的网络配置
		slipInfo = slip.ipconfig()
		print('slip ipconfig: ')
		print(slipInfo)
		if self.lteInfo != -1:
			# 设置默认网卡,当设置slip作为上网卡时不设置该接口，即SLIP_OUTER类型
			ret = slip.set_default_netif(self.lteInfo[2][2])
			if ret != 0:
				print('slip set default netif fail')
				return -1
		# 添加路由信息，设置网卡转发规则192.168.4.0表示ap的网段，255.255.255.0子网掩码
		ret = slip.router_add('192.168.4.0', '255.255.255.0')
		if ret != 0:
			print('slip add subnet routers fail')
			return -1
		return 0

	def set_ap(self,name=None,pwd=None,project_name='wifi_setap',project_version='1.0.0'):
		checknet = checkNet.CheckNetwork(project_name, project_version)
		stagecode, subcode = checknet.wait_network_connected(30)
		if stagecode != 3 or subcode != 1:
			print('fail to set ap. ')
			return -1
		# 创建一个socket实例
		sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
		# 增加端口复用
		sock.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
		# 解析域名
		addr = usocket.getaddrinfo(self.ESP_SERVER, self.ESP_SERVER_PORT)
		print(addr)
		sockaddr = addr[0][-1]
		print(sockaddr)
		bind_addr = ('172.16.1.2', 10001)
		ret = sock.bind(bind_addr)
		print('bind success')
		print(ret)
		# 建立连接
		sock.connect(sockaddr)
		# 向服务端发送消息
		if name == None and pwd == None:
			return -1
		elif name == None:
			msg = self._pack_tlv_format('F1', pwd)
		elif pwd == None:
			msg = self._pack_tlv_format('F2', name)
		else:
			msg = self._pack_tlv_format('F3', name+','+pwd)
		print(msg)
		ret = sock.send(msg)
		print('send %d bytes' % ret)
		# 接收服务端消息
		data = sock.recv(256)
		print('recv %s bytes:' % len(data))
		print(data.decode())

		# 关闭连接
		sock.close()
		return 0

	def wifi_off(self):
		slip.destroy()

if __name__=="__main__":
	esp8266 = Esp8266_ap(UART.UART2)
	esp8266.set_ap(name='大好年华',pwd='11111111')
	err = esp8266.wifi_on()
	if err == 0:
		print('slip network card create success')
	else:
		print('slip network card create fail')
