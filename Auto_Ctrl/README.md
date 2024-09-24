# 基于计算机视觉的AI滴定控制装置
## Mlabs AI Titration 1.0
## **[慕乐网络科技(大连)有限公司, MoolsNet](https://www.mools.net/)**

![Logo](组合logo.png?raw=true)

## 本文件夹存放自动滴定控制代码

**predictor_burette.py**： 是程序文件  

**resnet34-1Net.pth 等**： 是调用的权重文件，由训练程序获得

**class_indices.json**： 记录了分类信息，需要与训练程序一致   

**burette_clearair.py** 简单的电机控制程序，用来清空滴定管内的气泡

**burette_velocity.py** 简单的电机控制程序，用来调整主程序运行时阀门的开度，达到一滴一滴的效果

如果不清楚程序使用的串口号，请打开电脑的设备管理器-COM串口，找到对应的CH340串口对应的串口号或参考视频教程