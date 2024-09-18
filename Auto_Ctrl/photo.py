#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: photo.py
Author: Zinc Zou
Email: zincou@163.com
Date: 2024/9/3
Copyright: 慕乐网络科技(大连）有限公司
        www.mools.net
        moolsnet@126.com
Description: 
"""
import cv2


def main():
    # 初始化摄像头
    # 参数0通常表示计算机的默认摄像头
    # 如果你有多个摄像头，可以尝试其他数字来指定不同的摄像头
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    while True:
        # 逐帧捕获
        ret, frame = cap.read()

        # 如果正确读取帧，ret为True
        if not ret:
            print("无法接收帧 (流结束?). 退出...")
            break

            # 显示结果帧
        cv2.imshow('Frame', frame)

        # 按'q'键退出循环
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

            # 释放捕获器
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
