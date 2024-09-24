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


def get_picture(frame):  # 获取照片

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
    image_name = str(int(time.time())) + ".jpg"
    # 照片存储位置
    filepath = "Input/" + image_name  # 改成跟上面一样的位置
    str_name = filepath.replace('%s', label)
    cv2.imwrite(str_name, frame)    # 将照片保存起来

    return image_name


def start_move_1():  # 快速加酸程序

    port = "COM5"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改

    ser = serial.Serial(port, baudrate)
    data = b"q1h16d"  # 每分钟转16圈
    ser.write(data)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h3d"  # 逆时针
    ser.write(data)
    time.sleep(20)
    data = b"q6h2d"  # 顺时针
    ser.write(data)
    ser.close()


def start_move_2():  # 缓慢加酸程序

    port = "COM5"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改

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


def start_move_3():  # 停止加酸程序
    port = "COM5"  # 串口名，根据实际情况修改
    baudrate = 9600  # 波特率，根据实际情况修改

    ser = serial.Serial(port, baudrate)
    time.sleep(0.01)
    data = b"q5h1d"  # 转1秒
    ser.write(data)
    time.sleep(0.01)
    data = b"q6h2d"  # 顺时针
    ser.write(data)
    # 将阀门转回去
    ser.close()


def read_number_new(self, filepath, types):
    from paddleocr import PaddleOCR, draw_ocr

    # 创建一个OCR实例，配置语言为中文
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    # 对图片进行OCR识别
    img_path = filepath
    result = ocr.ocr(img_path, cls=True)
    print('-----------------------------------------')

    ans = []
    for line in result:
        for line1 in line:
            # print(line1[-1])
            # print(line1[-1][0])
            try:
                ans.append(int(line1[-1][0]))
            except:
                continue

    print(ans)
    return ans


def main():
    output_dir = "Output"
    filename = "bottle."
    model_type = "vit_b"
    device = "cuda"
    count = 0
    # # 快速滴加过程，这里请自己根据滴加量优化
    # while count < 14:
    #     start_move_1()
    #     time.sleep(3)
    #     count += 1
    # if count == 13:
    #     break
    videoSourceIndex = 0  # 摄像机编号，请根据自己的情况调整
    cap = cv2.VideoCapture(videoSourceIndex, cv2.CAP_DSHOW)  # 打开摄像头
    # 是否用GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # start_move_2()  # 开启慢滴状态
    # 循环开始之前需要一个变量来记录初始状态 比如说就叫color_type
    color_type = "colorless"

    while True:
        # 读取图片
        ret, frame = cap.read()
        name = get_picture(frame)
        # 图片完整路径
        im_file = 'Input/' + name
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)
        # 使用PIL库打开图片
        image = Image.open(im_file)
        # print(type(image)) # 打印图片的类型
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
        # 定义模型权重文件的路径
        json_path = './class_indices.json'

        with open(json_path, "r") as f:
            class_indict = json.load(f)
        # create model
        model = resnet34(num_classes=2).to(device)

        # load model weights
        weights_path = "./resnet34-1Net.pth"
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

        if class_a != color_type:  # 颜色不同
            # 关闭阀门
            # start_move_3()
            print('----->>End<<-----')
            print(im_file)
            time.sleep(1)
            # 释放摄像头
            cap.release()
            # 关闭所有OpenCV窗口
            cv2.destroyAllWindows()
            color_type = "orange"
            break
        time.sleep(.5)  # 拍照间隔


if True:
    main()
