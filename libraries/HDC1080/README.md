# HDC1080

**类引用：**

```python
from hdc1080 import Hdc1080
```



**实例化参数：**

| 名称     | 必填 | 类型 | 说明                    |
| -------- | ---- | ---- | ----------------------- |
| i2c_obj  | 是   | int  | i2c对象                 |
| dev_addr | 否   | int  | i2c从设备地址，默认0x40 |

```python
i2c_dev = I2C(I2C.I2C1, I2C.STANDARD_MODE)
hdc = Hdc1080(i2c_dev)
```

**接口函数：**

l **read()**

​	读取寄存器值转化成湿度和温度

参数：

​    无。

返回值：

| 名称                   | 类型  | 说明       |
| ---------------------- | ----- | ---------- |
| (humidity,temperature) | tuple | 湿度，温度 |

l **reset()**

​	重置hdc1080

参数：

​    无。

返回值：

​	无。
