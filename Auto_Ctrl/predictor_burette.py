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


def get_picture(cap):  # 获取照片

    # 捕获一帧的数据
    ret, frame = cap.read()
    if frame is None:
        print(frame)
    if ret:
        # 默认不阻塞
        cv2.imshow("picture", frame)
    # 数据帧写入图片中
    label = "1"
    timeStamp = 1381419600
    image_name = str(int(time.time())) + ".jpg"
    # 照片存储位置
    filepath = "Input/" + image_name  # 改成跟上面一样的位置
    str_name = filepath.replace('%s', label)
    cv2.imwrite(str_name, frame)    # 将照片保存起来

    return image_name


def start_move_1(port, baudrate):  # 快速加酸程序
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


def start_move_2(port, baudrate):  # 缓慢加酸程序
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


def start_move_3(port, baudrate):  # 停止加酸程序
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
    cap = cv2.VideoCapture(videoSourceIndex, cv2.CAP_DSHOW)  # 打开摄像头
    # name = get_picture()  # 获取照片
    # image_file = 'Input/M8RoIA3V.jpg'  # 测试时使用的指定照片作为输入
    # im_file = 'Input/' + name
    # image = cv2.imread(im_file)
    # 是否用GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    start_move_2(port, baudrate)  # 开启慢滴状态
    while True:
        # 读取图片
        name = get_picture(cap)
        # 图片完整路径
        im_file = 'Input/' + name
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
        if class_a == "orange" and prob_b >= 0.5:  # 到达滴定终点
            # 关闭阀门
            start_move_3(port, baudrate)
            print('----->>End<<-----')
            print(im_file)
            time.sleep(1)
            # 释放摄像头
            cap.release()
            # 关闭所有OpenCV窗口
            cv2.destroyAllWindows()

            break
        time.sleep(1)  # 拍照间隔


if True:
    main()