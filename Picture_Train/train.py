import os
import sys
import json

import torch
import torch.nn as nn
from torchvision import transforms, datasets
import torch.optim as optim
from tqdm import tqdm

from resnet import resnet34


# 主函数
def main():
    # 判断是否有可用的GPU，如果有则使用GPU，否则使用CPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # 定义训练和验证的数据变换
    data_transform = {
        "train": transforms.Compose([
            # 随机裁剪并缩放图片到224x224大小
            transforms.RandomResizedCrop(224),
            # 随机水平翻转图片
            transforms.RandomHorizontalFlip(),
            # 将图片转换为Tensor
            transforms.ToTensor(),
            # 对图片进行归一化
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]),
        "val": transforms.Compose([
            # 将图片缩放到224x224大小
            transforms.Resize((224, 224)),
            # 将图片转换为Tensor
            transforms.ToTensor(),
            # 对图片进行归一化
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])}

    # 获取数据集的根路径
    data_root = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    # 拼接出图片数据集的路径
    image_path = os.path.join(data_root, "AI-Titration\\Picture_Train", "data")
    # 断言图片数据集路径存在
    assert os.path.exists(image_path), "{} path does not exist.".format(image_path)

    # 加载训练数据集
    train_dataset = datasets.ImageFolder(root=os.path.join(image_path, "train"),
                                         transform=data_transform["train"])
    # 获取训练数据集中的样本数量
    train_num = len(train_dataset)

    # 获取类别到索引的映射
    flower_list = train_dataset.class_to_idx
    # 反转映射，得到索引到类别的映射
    cla_dict = dict((val, key) for key, val in flower_list.items())

    # 将索引到类别的映射写入json文件
    json_str = json.dumps(cla_dict, indent=4)
    with open('class_indices.json', 'w') as json_file:
        json_file.write(json_str)

        # 设置batch大小
    batch_size = 32
    # 计算每个进程使用的dataloader工作线程数
    nw = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
    print('Using {} dataloader workers every process'.format(nw))

    # 创建训练数据加载器，使用指定的批次大小、是否打乱数据以及工作线程数
    train_loader = torch.utils.data.DataLoader(train_dataset,
                                               batch_size=batch_size, shuffle=True,
                                               num_workers=0)
    # 创建验证数据集，使用ImageFolder加载指定目录下的图片，并应用相应的数据变换
    validate_dataset = datasets.ImageFolder(root=os.path.join(image_path, "val"),
                                            transform=data_transform["val"])
    # 获取验证数据集的样本数量
    val_num = len(validate_dataset)
    # 创建验证数据加载器
    validate_loader = torch.utils.data.DataLoader(validate_dataset,
                                                  batch_size=batch_size, shuffle=False,
                                                  num_workers=0)
    # 打印用于训练和验证的图片数量
    print("using {} images for training, {} images for validation.".format(train_num,
                                                                           val_num))
    # 创建一个验证数据加载器的迭代器，并获取一张图片和对应的标签（这里并未使用）
    # test_data_iter = iter(validate_loader)
    # test_image, test_label = test_data_iter.next()

    # 定义模型名称
    model_name = "3_Color_Model_"
    # 实例化ResNet34模型，并设置输出类别数为3
    net = resnet34(num_classes=2)
    # 将模型移动到指定的设备上（CPU或GPU）
    net.to(device)
    # 定义损失函数为交叉熵损失
    loss_function = nn.CrossEntropyLoss()
    # 定义优化器为Adam，并设置学习率为0.0001
    optimizer = optim.Adam(net.parameters(), lr=0.0001)
    # 设置训练轮数
    epochs = 10
    # 初始化最佳准确率为0
    best_acc = 0.0
    # 定义模型保存路径
    save_path = './{}Net.pth'.format(model_name)
    # 获取训练数据加载器的长度，即训练步数
    train_steps = len(train_loader)
    # 开始训练循环
    for epoch in range(epochs):
        # 设置模型为训练模式
        net.train()
        # 初始化训练损失为0
        running_loss = 0.0
        # 使用tqdm库创建一个进度条，用于显示训练进度
        train_bar = tqdm(train_loader, file=sys.stdout)
        # 开始训练步骤的循环
        for step, data in enumerate(train_bar):
            # 从数据加载器中获取图片和标签
            images, labels = data
            # 清空梯度
            optimizer.zero_grad()
            # 将图片和标签移动到指定的设备上
            outputs = net(images.to(device))
            # 计算损失
            loss_a = loss_function(outputs, labels.to(device))
            # 反向传播计算梯度
            loss_a.backward()
            # 使用优化器更新模型参数
            optimizer.step()
            # 累加训练损失
            running_loss += loss_a.item()
            # 更新进度条的描述，显示当前训练轮数、总轮数和损失值
            train_bar.desc = "train epoch[{}/{}] loss:{:.3f}".format(epoch + 1,
                                                                     epochs,
                                                                     loss_a)
        # 进入验证阶段
        net.eval()  # 将模型设置为评估模式，关闭dropout和batch normalization的某些行为
        acc = 0.0  # 初始化累计正确的数量，用于计算准确率
        # 不计算梯度，因为验证阶段不需要反向传播
        with torch.no_grad():
            val_bar = tqdm(validate_loader, file=sys.stdout)  # 创建验证数据加载器的进度条
            for val_data in val_bar:  # 遍历验证数据
                val_images, val_labels = val_data  # 获取验证图片和标签
                outputs = net(val_images.to(device))  # 前向传播，得到预测输出
                predict_y = torch.max(outputs, dim=1)[1]  # 获取预测的最大概率对应的类别索引
                acc += torch.eq(predict_y, val_labels.to(device)).sum().item()  # 计算预测正确的数量，并累加
        # 计算验证准确率
        val_accurate = acc / val_num
        # 打印当前轮数的训练损失和验证准确率
        print('[epoch %d] train_loss: %.3f  val_accuracy: %.3f' %
              (epoch + 1, running_loss / train_steps, val_accurate))
        # 如果当前验证准确率比之前保存的最高准确率还要高
        if val_accurate > best_acc:
            best_acc = val_accurate  # 更新最高准确率
            torch.save(net.state_dict(), save_path)  # 保存当前模型状态字典到指定路径
        # 训练完成后打印结束信息
        print('Finished Training')


if __name__ == '__main__':
    main()
