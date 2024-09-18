import time
import serial
import numpy as np
from paddleocr import PaddleOCR
import re
import cv2
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def main():
    output_dir = "Output"
    filename = "bottle."
    model_type = "vit_b"
    device = "cuda"
    count = 0
    port = "COM3"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改
    # # 快速滴加过程，这里请自己根据滴加量优化
    # start_move_1(port, baudrate)
    # time.sleep(15)
    videoSourceIndex = 0  # 摄像机编号，请根据自己的情况调整
    # 初始化摄像头
    cap = cv2.VideoCapture(videoSourceIndex, cv2.CAP_DSHOW)
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()
        # 创建一个窗口来显示视频
    # 不断读取摄像头的帧
    # start_move_2(port, baudrate)
    dianwei_list = []
    # 创建一个OCR实例，配置语言为中文
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    while True:
        # 读取一帧
        ret, frame = cap.read()
        # 如果读取失败，可能是因为摄像头被拔掉或其他原因
        if not ret:
            print("无法接收画面...退出...")
            break

        name = get_picture(frame)  # 获取照片
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)
        # '''
        # 图片完整路径
        im_file = 'Input/' + name
        # cv2.imshow('Video', im_file)
        # 定义模型权重文件的路径
        dianwei = read_number_new(im_file,ocr)
        # dianwei = dianwei[0]
        if dianwei_list:
            if dianwei < dianwei_list[-1] or dianwei > dianwei_list[-1] * 2:
                dianwei = dianwei_list[-1]
        elif dianwei < 50:
            continue
        print(dianwei)
        dianwei_list.append(dianwei)
        try:
            if 500 >= dianwei >= 300:  # 到达滴定终点
                # 关闭阀门
                # start_move_3(port, baudrate)
                print('----->>End<<-----')
                print(im_file)
                time.sleep(1)
                # 释放摄像头
                cap.release()
                # 关闭所有OpenCV窗口
                cv2.destroyAllWindows()
                print(dianwei_list)
                break
            if dianwei <= 0:
                break
        except:
            print(dianwei_list)
    # 释放摄像头资源
    cap.release()
    # 关闭所有OpenCV创建的窗口
    cv2.destroyAllWindows()
    return dianwei_list


def get_picture(frame):  # 获取照片
    # 数据帧写入图片中
    label = "1"
    timeStamp = 1381419600
    # image_name = "PH" + str(int(time.time())) + ".jpg"
    image_name = "PH" + str(987654321) + ".jpg"
    # 照片存储位置
    filepath = "Input/" + image_name  # 改成跟上面一样的位置
    str_name = filepath.replace('%s', label)
    cv2.imwrite(str_name, frame)  # 将照片保存起来
    return image_name


def start_move_1(port="COM9", baudrate=9600, sleep_time=5):  # 快速加酸程序
    ser = serial.Serial(port, baudrate)
    data = b"q1h16d"  # 每分钟转16圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h3d"  # 逆时针
    ser.write(data)
    time.sleep(sleep_time)
    data = b"q6h2d"  # 顺时针
    ser.write(data)
    ser.close()


def start_move_2(port="COM9", baudrate=9600):  # 缓慢加酸程序
    ser = serial.Serial(port, baudrate)
    data = b"q1h15d"  # 每分钟转6圈，每秒0.1圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h3d"  # 逆时针
    ser.write(data)
    # 注意，这里没有将阀门转回去，而是持续几秒钟滴加一次的状态
    ser.close()


def start_move_3(port="COM9", baudrate=9600):  # 停止加酸程序
    ser = serial.Serial(port, baudrate)
    data = b"q1h15d"  # 每分钟转6圈，每秒0.1圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h2d"  # 顺时针
    ser.write(data)
    # 将阀门转回去
    ser.close()


# 定义多项式函数
def poly_func(x, a, b, c, d):
    return a * np.tanh(0.05*(x + b)) + c


def read_number_new(filepath,ocr):
    # 对图片进行OCR识别
    img_path = filepath
    result = ocr.ocr(img_path, cls=True)
    print('-----------------------------------------')
    # print(result)
    ans = []
    if result[0]:
        for line in result:
            for line1 in line:
                print(line1[-1])
                # print(line1[-1])
                # print(line1[-1][0])
                try:
                    ans.append(line1[-1][0])
                except:
                    continue
    else:
        ans = ['1']

    digits_regex = re.compile(r'^\d+$')  # 匹配从开始到结束都是数字的字符串
    filtered_digits = [s for s in ans if digits_regex.match(s)]
    if filtered_digits:
        concatenated_str = ''.join(filtered_digits)
        result = int(concatenated_str)
        print(result)
    else:
        print("列表中没有数字")
        result = 10
    print(result)
    return result

# '''
dianwei_list = main()
'''

dianwei_list = [46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 47, 47, 47, 47, 47, 48, 48, 48, 48, 48, 48,
                48, 48, 48, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 50, 50, 50, 50, 50, 50, 50, 51, 51, 51, 51, 52, 52,
                52, 52, 53, 53, 53, 54, 54, 54, 55, 55, 56, 56, 56, 57, 57, 57, 57, 58, 58, 58, 58, 59, 59, 59, 60, 60,
                60, 60, 61, 61, 61, 61, 62, 62, 62, 62, 63, 63, 63, 64, 64, 64, 64, 65, 65, 65, 65, 66, 66, 66, 66, 67,
                67, 67, 67, 67, 68, 68, 68, 68, 69, 69, 69, 69, 70, 70, 70, 70, 70, 71, 71, 71, 71, 72, 72, 73, 73, 74,
                74, 74, 75, 75, 76, 76, 77, 77, 78, 78, 79, 79, 80, 80, 81, 81, 81, 82, 83, 83, 83, 84, 86, 86, 87, 87,
                88, 88, 89, 89, 90, 90, 91, 91, 92, 93, 93, 94, 94, 95, 96, 96, 97, 98, 98, 98, 99, 100, 100, 101, 101,
                102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
                123, 125, 126, 127, 129, 130, 132, 133, 135, 136, 137, 139, 140, 141, 142, 143, 144, 146, 147, 149, 151,
                152, 154, 155, 157, 159, 163, 167, 170, 179, 179, 184, 190, 199, 217, 229, 253, 299, 315, 320, 336, 342,
                346, 351, 354, 356, 358, 359, 361, 362, 363, 364, 365, 366, 367, 367, 368, 369, 369, 370, 371]
'''
x = []
y = dianwei_list
y1 = [0]
y2 = [0]
for i in range(len(dianwei_list)):
    x.append(i)

# 初始参数估计
popt, pcov = curve_fit(poly_func, x, y, p0=[50, -250, 200, 1])
# popt, pcov = curve_fit(poly_func, x, y, p0=[1, 1, 1,1])

# 打印最优参数
print("最优参数:", popt)
print('突跃点：', -popt[1], popt[2])

# 使用拟合得到的参数绘制曲线
x_fit = np.linspace(min(x), max(x), 500)
y_fit = poly_func(x_fit, *popt)
# 计算一阶微商（即电位对体积的导数）
dE_dV = np.gradient(y_fit)
# 计算二阶微商
d2E_dV2 = np.gradient(dE_dV)
y2 = d2E_dV2.tolist()
# y2 = [round(x1, 0) for x1 in x_fit]

data_dict = {}
fig, ax1 = plt.subplots()
plt.title("potential function")
# 绘制第一个Y轴的数据
color = 'tab:red'
ax1.set_xlabel('x data')
ax1.set_ylabel('y data', color=color)
ax1.plot(x, y, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# 创建一个共享X轴的第二个Y轴
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('y2 data', color=color)
ax2.plot(x_fit, y2, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # 自动调整子图参数, 使之填充整个图像区域
plt.show()

# '''
