import torch
from ultralytics import YOLO
import cv2
import time
import serial
    
# 打开摄像头
videoSourceIndex = 0       # 摄像机编号，0或1
cap = cv2.VideoCapture(videoSourceIndex, cv2.CAP_DSHOW)  # 打开摄像头

# 打印初始系统时间
start_time = time.time()
print("比赛初始时间:", time.ctime(start_time))

# 载入模型
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO('best.pt')
model.to(device)
# 打开视频源
#cap = cv2.VideoCapture('e7c3d6ecda62a8dc160f98f3173f9cf4.mp4')

# 存储过去5帧中检测到的对象
recent_detections = []

# 每次按照设备管理器-更改串口COM的名称

def start_move_1():  # 快速加酸程序

    port = "COM4"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改

    ser = serial.Serial(port, baudrate)
    data = b"q1h15d"  # 每分钟转16圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h3d"  # 逆时针
    ser.write(data)
    ser.close()


def start_move_2():  # 缓慢加酸程序

    port = "COM4"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改

    ser = serial.Serial(port, baudrate)
    data = b"q1h9d"  # 每分钟转6圈，每秒0.1圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)  
    data = b"q6h3d"  # 逆时针
    ser.write(data)
    # 注意，这里没有将阀门转回去，而是持续几秒钟滴加一次的状态
    ser.close()


def start_move_3():  # 停止加酸程序
    port = "COM4"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改
    ser = serial.Serial(port, baudrate)
    data = b"q1h11d"  # 每分钟转6圈，每秒0.1圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h3d"  # 顺时针
    ser.write(data)
    # 将阀门转回去
    ser.close()
    

import time
import cv2

seen_one = False
seen_two = False
ignore_remaining = False
last_label = None
start_time_move_1 = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    
    detected = False
    final_label = None
    
    #逐帧检测最高置信度的分类
    if results and any(r.boxes for r in results):
        for r in results:
            if r.boxes:
                detected = True
                detect = sorted(r.boxes, key=lambda x: x.conf, reverse=True)[0]
                conf = detect.conf.item()
                label = detect.cls.item()
                
                if label == 0.0:
                    label_name = "transition"
                elif label == 1.0:
                    label_name = "yellow"
                elif label == 2.0:
                    label_name = "orange"
                
                print("label: ", label_name)
                print("confidence: ", conf)
                
                # 更新最近的检测结果列表
                recent_detections.append(label)

                if len(recent_detections) > 5:
                    recent_detections.pop(0)

                count = {cls: recent_detections.count(cls) for cls in set(recent_detections)}

                if count:
                    final_label = max(count, key=count.get)
                    print(f"The most frequent in the last 5 frames is: {final_label}")

                if final_label == 2.0:
                    # 如果检测到2.0，立即执行start_move_3()并结束循环
                    start_move_3()
                    end_time = time.time()
                    cap.release()
                    cv2.destroyAllWindows()
                    break

    # 强制执行start_move_1()快滴
    if not seen_one:
        start_move_1()
        start_time_move_1 = time.time()
        seen_one = True
        last_label = 1.0
        
    # 检查是否需要强制执行start_move_2() 
    if seen_one and not seen_two and time.time() - start_time_move_1 > 4.3:
        start_move_2()
        seen_two = True
        ignore_remaining = True
        last_label = 0.0
    
    # 根据条件执行不同的动作
    if not ignore_remaining:
        if final_label == 1.0:
            # 如果检测到1.0，不执行任何操作
            pass
        elif final_label == 0.0:
            # 如果检测到0.0，执行start_move_2()，并标记ignore_remaining为True
            start_move_2()
            ignore_remaining = True
            last_label = 0.0

                                     
    if not detected:
        print("No detections in the current frame")

    # 展示检测后的帧
    cv2.imshow('YOLOv8 Detection', frame)
    if cv2.waitKey(1) == ord('q'):
        break

# 打印最终系统时间
print("比赛开始时间:", time.ctime(start_time))
print("比赛结束时间:", time.ctime(end_time))

# 计算用时
elapsed_time = end_time - start_time
print("比赛用时:", elapsed_time, "秒")