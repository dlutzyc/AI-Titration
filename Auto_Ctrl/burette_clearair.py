import serial
import time

port = "COM5"  # 串口名，根据实际情况修改
baudrate = 9600  # 波特率

ser = serial.Serial(port, baudrate)

data = b"q1h16d"  # 设定为每分钟转16圈的模式，比慢滴模式角度稍微大一点点
ser.write(data)
time.sleep(0.01)

data = b"q5h1d"  # 转1秒
ser.write(data)
time.sleep(0.01)

data = b"q6h3d"  # 逆时针
ser.write(data)
time.sleep(3.01)    # 这个等待时间决定了阀门开启时间

data = b"q6h2d"  # 顺时针
ser.write(data)

ser.close() # 关闭串口
