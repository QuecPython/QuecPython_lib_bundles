import MCP2515
import utime
import _thread
from machine import Pin

mcp2515 = MCP2515(0, Pin.GPIO21, 500, 512)
can_frame_cnt = 0


def read_can_frame_thread():
    while True:
        frame_num = mcp2515.get_frame_number()
        if frame_num > 0:
            can_data = mcp2515.read(frame_num)
            global can_frame_cnt
            can_frame_cnt = can_frame_cnt + frame_num
            print("can_frame_cnt: {}".format(can_frame_cnt))
        utime.sleep_ms(100)


if __name__ == "__main__":
    _thread.start_new_thread(read_can_frame_thread, ())
    send_cnt = 0
    while True:
        if send_cnt < 1000:
            send_bytearr = bytearray(2)
            send_bytearr[1] = send_cnt & 0xff
            send_bytearr[0] = (send_cnt>>8) & 0xff
            mcp2515.write(0x6FF, 0, 0, bytes(send_bytearr))
            utime.sleep_ms(500)
            send_cnt = send_cnt +1
        else:
            print("send finish,cnt:", send_cnt)
            break
            