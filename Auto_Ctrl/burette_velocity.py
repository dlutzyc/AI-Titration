import serial
import time

port = "COM5"  # 串口名，根据实际情况修改
baudrate = 9600  # 波特率，根据实际情况修改

ser = serial.Serial(port, baudrate)
data = b"q1h14d"
ser.write(data)
time.sleep(0.01)
data = b"q2h90d"
ser.write(data)
time.sleep(0.01)
# 以上是逆时针旋转的速度参数，可以反复调节，以达到逐滴滴定的效果

data = b"q5h1d"  # 转1秒
ser.write(data)
time.sleep(0.01)

data = b"q6h3d"  # 逆时针
ser.write(data)
time.sleep(5.01)    # 这里的等待时间决定了阀门开启时间，不能小于1秒（也就是阀门转开的时间）

data = b"q1h15d"  # 回转的速度参数，建议与主程序中慢滴的速度一致，保证正反转角度一致
ser.write(data)
time.sleep(0.01)

data = b"q2h0d"
ser.write(data)
time.sleep(0.01)

data = b"q6h2d"  # 顺时针
ser.write(data)

ser.close()
