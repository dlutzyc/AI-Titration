import torch
from PIL import Image
import torchvision.transforms as transforms
from torch.autograd import Variable
from torch import nn
import matplotlib.pyplot as plt
import cv2
import time
import os
from model import resnet34
import json
import serial
from datetime import datetime
from scipy.optimize import curve_fit
import numpy as np
import re


def get_picture(frame, typ=0,date=''):  # 获取照片

    # 捕获一帧的数据
    # ret, frame = cap.read()
    if frame is None:
        print(frame)
    # if ret:
    #     # 默认不阻塞
    #     cv2.imshow("picture", frame)
    # 数据帧写入图片中
    label = "1"
    timeStamp = 1381419600
    if typ:
        image_name = f'{date}{int(time.time())}.jpg'
    else:
        image_name = f'{date}PH{int(time.time())}.jpg'
    # 照片存储位置
    filepath = "Input/" + image_name  # 改成跟上面一样的位置
    str_name = filepath.replace('%s', label)
    cv2.imwrite(str_name, frame)  # 将照片保存起来

    return image_name


def start_move_1(ser):  # 抽取原料
    # 注意：这里我们将控制器的模式切换成了20ml注射泵模式，由于丝杠的区别，这里设定的速度为实际速度（ml/min）的一半
    data = b"q1h12d"  # 每分钟加样24ml
    ser.write(data)
    time.sleep(0.01)
    data = b"q4h0d"  # 转0分钟
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h30d"  # 转30秒
    ser.write(data)  # 合计抽取12ml
    time.sleep(0.01)
    data = b"q6h3d"  # 抽取
    ser.write(data)
    time.sleep(30)  # 等待抽取
    print('完成抽取')
    # ser.close()


def start_move_2(ser):  # 缓慢加样程序
    data = b"q1h3d"  # 每分钟加样6ml，每秒0.1ml
    ser.write(data)
    time.sleep(0.01)
    data = b"q4h0d"  # 转0分钟
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)  # 合计进样12ml
    time.sleep(0.01)
    data = b"q6h2d"  # 进样
    ser.write(data)
    time.sleep(1)
    # 注意，这里没有将阀门转回去，而是持续几秒钟滴加一次的状态
    # ser.close()


def start_move_3(ser):  # 停止加酸程序
    data = b"q6h6d"  # 停止指令
    ser.write(data)
    # 将阀门转回去
    ser.close()


def read_number_new(filepath):
    from paddleocr import PaddleOCR, draw_ocr
    # 创建一个OCR实例，配置语言为中文
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    # 对图片进行OCR识别
    img_path = filepath
    result = ocr.ocr(img_path, cls=True)
    print('-----------------------------------------')
    print(result)
    ans = []
    for line in result:
        if line:
            for line1 in line:
                # print(line1[-1])
                # print(line1[-1][0])
                try:
                    ans.append(float(line1[-1][0]))
                except:
                    continue
    print(ans)
    if not ans:
        ans.append(10)
    return ans

# 定义反正切函数
def poly_func(x, a, b, c, d):
    return a * np.tanh(0.05*(x + b)) + c


def line_chart(date = "1", valume_list = [], voltage_list = [], color_list = []):
    x = valume_list
    y = voltage_list
    z = []

    for color in color_list:
        color = re.sub(r'\d+\.?\d*', '', color)
        if color == 'yellow':
            z.append(0)
        else:
            z.append(1)
    # '''
    # 初始参数估计
    popt, pcov = curve_fit(poly_func, x, y, p0=[15, -200, 1, 1])

    # 打印最优参数
    print("最优参数:", popt)
    print('突跃点：', -popt[1], popt[2])

    # 使用拟合得到的参数计算二阶导数
    y_fit = poly_func(x, *popt)
    # 计算一阶微商（即电位对体积的导数）
    dE_dV = np.gradient(y_fit)
    # 计算二阶微商
    d2E_dV2 = np.gradient(dE_dV)
    y2 = d2E_dV2.tolist()
    # '''
    fig, ax1 = plt.subplots()
    plt.title("titration curve")
    # 绘制第一个Y轴的数据
    color = 'tab:red'
    ax1.set_xlabel('valume')
    ax1.set_ylabel('voltage', color=color)
    ax1.plot(x, y, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # 创建一个共享X轴的第二个Y轴
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('color', color=color)
    ax2.plot(x, z, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # 自动调整子图参数, 使之填充整个图像区域
    # plt.savefig(f'Output/{date}.png')
    plt.savefig('1.png')
    plt.show()


def main():
    output_dir = "Output"
    filename = "bottle."
    model_type = "vit_b"
    device = "cuda"
    count = 0
    port_pump = "COM8"  # 注射泵串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改
    pump_ser = serial.Serial(port_pump, baudrate)
    start_move_1(pump_ser)
    videoSourceIndex = 0  # 摄像机编号，请根据自己的情况调整
    videoSourceIndex_1 = 2  # 摄像机编号，请根据自己的情况调整
    cap = cv2.VideoCapture(videoSourceIndex, cv2.CAP_DSHOW)  # 打开摄像头
    cap_1 = cv2.VideoCapture(videoSourceIndex_1, cv2.CAP_DSHOW)  # 打开摄像头2
    # 是否用GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    start_move_2(pump_ser)  # 开启慢滴状态
    # 循环开始之前需要一个变量来记录初始状态 比如说就叫color_type
    total_valume = 0
    valume_list = []
    voltage_list = []
    color_list = []
    start_time = time.time()
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(start_time)
    # 格式化datetime对象为字符串，该时间用于保存图像名称
    formatted_time = dt_object.strftime('%Y%m%d_%H%M%S')
    print("实验开始于", formatted_time)
    n = 15
    while True:
        start_move_2(pump_ser)  # 开启慢滴状态
        total_valume += 0.1
        total_valume = round(total_valume, 1)
        # 读取图片
        ret, frame = cap.read()
        ret_1, frame_1 = cap_1.read()
        name = get_picture(frame, 0, formatted_time)
        name_1 = get_picture(frame_1, 1, formatted_time)

        # 图片完整路径
        im_file = 'Input/' + name
        im_file_1 = 'Input/' + name_1
        cv2.imshow('Color', frame)
        cv2.waitKey(1)
        cv2.imshow('Number', frame_1)
        cv2.waitKey(1)
        # 使用PIL库打开图片
        image = Image.open(im_file)
        # 定义图片预处理流程
        data_transform = transforms.Compose(
            [
                # 调整图片大小为256x256
                transforms.Resize(256),
                # 从中心裁剪出224x224大小的图片
                transforms.CenterCrop(224),
                # 将图片转换为PyTorch的Tensor格式
                transforms.ToTensor(),
                # 对图片进行归一化，使用ImageNet的均值和标准差
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        # [N, C, H, W]
        img = data_transform(image)
        # expand batch dimension
        img = torch.unsqueeze(img, dim=0)
        # 定义模型分类文件的路径
        json_path = './class_indices.json'

        with open(json_path, "r") as f:
            class_indict = json.load(f)
        # create model
        model = resnet34(num_classes=2).to(device)  # 根据分类数量修改

        # load model weights
        weights_path = "./resnet5-15Net.pth"  # 根据实际需要使用的模型名称修改
        assert os.path.exists(weights_path), "file: '{}' dose not exist.".format(weights_path)
        model.load_state_dict(torch.load(weights_path, map_location=device))

        # prediction
        model.eval()
        with torch.no_grad():
            # predict class
            output = torch.squeeze(model(img.to(device))).cpu()
            # 对预测结果进行softmax，得到每个类别的概率
            predict = torch.softmax(output, dim=0)
            # 找到概率最大的类别的索引
            predict_cla = torch.argmax(predict).numpy()
        # 根据索引从类别字典中获取类别名称
        class_a = "{}".format(class_indict[str(predict_cla)])
        # 格式化概率值，保留三位小数
        prob_a = "{:.3}".format(predict[predict_cla].numpy())
        # 将概率值转换为浮点数
        prob_b = float(prob_a)
        # 打印预测的类别和概率
        print(class_a)
        print(prob_b)
        valume_list.append(total_valume)
        # print(read_number_new(im_file_1))
        color_list.append(class_a + str(prob_b))
        voltage = read_number_new(im_file_1)[0]
        if voltage_list:
            if voltage < voltage_list[-1]:
                voltage = voltage_list[-1]
        voltage_list.append(voltage)
        if class_a == "orange":  # 判断终点
            if n == 15:
                print(im_file)
            n += -1
        if n <= 0:  # 判断终点
            # 关闭阀门
            start_move_3(pump_ser)
            print('----->>End<<-----')

            time.sleep(1)
            # 释放摄像头
            cap.release()
            cap_1.release()
            # 关闭所有OpenCV窗口
            cv2.destroyAllWindows()
            break
        if (total_valume % 12) == 0:
            start_move_1(pump_ser)
        print(total_valume)
        time.sleep(.5)  # 拍照间隔

    print(valume_list)
    print(voltage_list)
    print(color_list)

    line_chart(formatted_time, valume_list, voltage_list, color_list)


if True:
    # main()
    line_chart()