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
    x =[0.1, 0.2, 0.30000000000000004, 0.4, 0.5, 0.6, 0.7, 0.7999999999999999, 0.8999999999999999, 0.9999999999999999,
     1.0999999999999999, 1.2, 1.3, 1.4000000000000001, 1.5000000000000002, 1.6000000000000003, 1.7000000000000004,
     1.8000000000000005, 1.9000000000000006, 2.0000000000000004, 2.1000000000000005, 2.2000000000000006,
     2.3000000000000007, 2.400000000000001, 2.500000000000001, 2.600000000000001, 2.700000000000001, 2.800000000000001,
     2.9000000000000012, 3.0000000000000013, 3.1000000000000014, 3.2000000000000015, 3.3000000000000016,
     3.4000000000000017, 3.5000000000000018, 3.600000000000002, 3.700000000000002, 3.800000000000002, 3.900000000000002,
     4.000000000000002, 4.100000000000001, 4.200000000000001, 4.300000000000001, 4.4, 4.5, 4.6, 4.699999999999999,
     4.799999999999999, 4.899999999999999, 4.999999999999998, 5.099999999999998, 5.1999999999999975, 5.299999999999997,
     5.399999999999997, 5.4999999999999964, 5.599999999999996, 5.699999999999996, 5.799999999999995, 5.899999999999995,
     5.999999999999995, 6.099999999999994, 6.199999999999994, 6.299999999999994, 6.399999999999993, 6.499999999999993,
     6.5999999999999925, 6.699999999999992, 6.799999999999992, 6.8999999999999915, 6.999999999999991, 7.099999999999991,
     7.19999999999999, 7.29999999999999, 7.39999999999999, 7.499999999999989, 7.599999999999989, 7.699999999999989,
     7.799999999999988, 7.899999999999988, 7.999999999999988, 8.099999999999987, 8.199999999999987, 8.299999999999986,
     8.399999999999986, 8.499999999999986, 8.599999999999985, 8.699999999999985, 8.799999999999985, 8.899999999999984,
     8.999999999999984, 9.099999999999984, 9.199999999999983, 9.299999999999983, 9.399999999999983, 9.499999999999982,
     9.599999999999982, 9.699999999999982, 9.799999999999981, 9.89999999999998, 9.99999999999998, 10.09999999999998,
     10.19999999999998, 10.29999999999998, 10.399999999999979, 10.499999999999979, 10.599999999999978,
     10.699999999999978, 10.799999999999978, 10.899999999999977, 10.999999999999977, 11.099999999999977,
     11.199999999999976, 11.299999999999976, 11.399999999999975, 11.499999999999975, 11.599999999999975,
     11.699999999999974, 11.799999999999974, 11.899999999999974, 11.999999999999973, 12.099999999999973,
     12.199999999999973, 12.299999999999972, 12.399999999999972, 12.499999999999972, 12.599999999999971,
     12.69999999999997, 12.79999999999997, 12.89999999999997, 12.99999999999997, 13.09999999999997, 13.199999999999969,
     13.299999999999969, 13.399999999999968, 13.499999999999968, 13.599999999999968, 13.699999999999967,
     13.799999999999967, 13.899999999999967, 13.999999999999966, 14.099999999999966, 14.199999999999966,
     14.299999999999965, 14.399999999999965, 14.499999999999964, 14.599999999999964]
    y = [96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 96.0, 97.0, 98.0, 98.0, 98.0, 98.0, 98.0, 98.0, 98.0,
     99.0, 99.0, 100.0, 100.0, 100.0, 101.0, 101.0, 101.0, 102.0, 102.0, 102.0, 103.0, 103.0, 103.0, 104.0, 104.0,
     104.0, 105.0, 105.0, 106.0, 106.0, 107.0, 107.0, 107.0, 108.0, 108.0, 109.0, 109.0, 110.0, 110.0, 111.0, 111.0,
     111.0, 112.0, 112.0, 113.0, 113.0, 114.0, 114.0, 115.0, 116.0, 116.0, 117.0, 118.0, 118.0, 119.0, 120.0, 120.0,
     121.0, 121.0, 122.0, 123.0, 124.0, 125.0, 125.0, 126.0, 127.0, 128.0, 129.0, 130.0, 131.0, 132.0, 133.0, 134.0,
     135.0, 136.0, 138.0, 139.0, 142.0, 143.0, 145.0, 145.0, 146.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0,
     153.0, 153.0, 154.0, 154.0, 155.0, 155.0, 156.0, 156.0, 157.0, 158.0, 159.0, 159.0, 159.0, 159.0, 160.0, 160.0,
     161.0, 161.0, 162.0, 163.0, 169.0, 166.0, 168.0, 169.0, 170.0, 171.0, 173.0, 176.0, 177.0, 179.0, 181.0, 182.0,
     184.0, 185.0, 189.0, 190.0, 192.0, 196.0, 198.0, 200.0, 201.0, 205.0, 210.0, 216.0, 223.0, 229.0, 239.0]
    color_list = ['yellow0.999', 'yellow0.986', 'yellow0.993', 'yellow0.991', 'yellow0.991', 'yellow0.995', 'yellow0.997',
     'yellow0.994', 'yellow0.995', 'yellow0.998', 'yellow0.998', 'yellow0.998', 'yellow0.997', 'yellow0.995',
     'yellow0.996', 'yellow0.998', 'yellow0.998', 'yellow0.993', 'yellow0.996', 'yellow0.995', 'yellow0.995',
     'yellow0.987', 'yellow0.995', 'yellow0.995', 'yellow0.995', 'yellow0.995', 'yellow0.986', 'yellow0.982',
     'yellow0.989', 'yellow0.981', 'yellow0.997', 'yellow0.998', 'yellow0.996', 'yellow0.998', 'yellow0.992',
     'yellow0.991', 'yellow0.994', 'yellow0.998', 'yellow0.996', 'yellow0.978', 'yellow0.997', 'yellow0.996',
     'yellow0.998', 'yellow0.993', 'yellow0.993', 'yellow0.993', 'yellow0.992', 'yellow0.996', 'yellow0.997',
     'yellow0.997', 'yellow0.996', 'yellow0.996', 'yellow0.998', 'yellow0.998', 'yellow0.997', 'yellow0.996',
     'yellow0.996', 'yellow0.988', 'yellow0.956', 'yellow0.99', 'yellow0.989', 'yellow0.99', 'yellow0.992',
     'yellow0.992', 'yellow0.992', 'yellow0.991', 'yellow0.986', 'yellow0.996', 'yellow0.988', 'yellow0.986',
     'yellow0.99', 'yellow0.996', 'yellow0.995', 'yellow0.995', 'yellow0.995', 'yellow0.987', 'yellow0.987',
     'yellow0.984', 'yellow0.997', 'yellow0.997', 'yellow0.997', 'yellow0.996', 'yellow0.996', 'yellow0.994',
     'yellow0.995', 'yellow0.984', 'yellow0.942', 'yellow0.948', 'yellow0.952', 'yellow0.991', 'yellow0.929',
     'yellow0.985', 'yellow0.984', 'yellow0.957', 'yellow0.978', 'yellow0.95', 'yellow0.973', 'yellow0.983',
     'yellow0.997', 'yellow0.997', 'yellow0.998', 'yellow0.996', 'yellow0.996', 'yellow0.997', 'yellow0.998',
     'yellow0.999', 'yellow0.996', 'yellow0.996', 'yellow0.997', 'yellow0.997', 'yellow0.999', 'yellow0.999',
     'yellow0.998', 'yellow0.999', 'yellow0.999', 'yellow0.999', 'yellow0.996', 'yellow0.999', 'yellow0.999',
     'yellow0.999', 'yellow0.998', 'yellow0.999', 'yellow0.991', 'yellow0.954', 'yellow0.833', 'yellow0.715',
     'yellow0.765', 'yellow0.842', 'yellow0.749', 'yellow0.655', 'yellow0.601', 'orange0.642', 'orange0.767',
     'orange0.723', 'orange0.882', 'orange0.832', 'orange0.887', 'orange0.847', 'orange0.926', 'orange0.968',
     'orange0.917', 'orange0.927', 'orange0.962', 'orange0.968', 'orange0.898', 'orange0.929']
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