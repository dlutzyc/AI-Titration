#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout
from qt_VisualReadScale_window import Ui_UITitrationbyReadScale
from DDInterface import DDInterface
from qt_prompt_window import Ui_Prompt
from PyQt5 import QtCore
import sys
import time
from PyQt5.QtCore import QTimer, QTime
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from DDParams import DDParams
from QSSLoader import QSSLoader

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

import random
from RunningSetting import RunningSetting


# 读刻度线


class UITitrationbyReadScale(QMainWindow, Ui_UITitrationbyReadScale):
    TAG = "<UITitrationbyReadScale>  "

    def __init__(self, myDDParams):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        if sys.platform.startswith('linux'):
            self.showFullScreen()
        self.myDDParams = myDDParams
        self.bt_finish.hide()
        self.bt_continue.hide()
        self.bt_stop.clicked.connect(self.stopDD)
        self.bt_pause.clicked.connect(self.pauseDD)
        self.bt_continue.clicked.connect(self.continueDD)
        self.bt_finish.clicked.connect(self.BackMain)
        self.stackedWidget.setCurrentIndex(0)

        # self.startTimer()
        # self.startDD(self.myDDParams)
        self.line_x = []
        self.line_1_y = []
        self.line_2_y = []
        self.timex = 1
        self.DrawLine()

    def stopDD(self):
        self.stopTimer()
        # self.myDD.stopDD()
        pass

    def pauseDD(self):
        # self.bt_continue.show()
        # self.bt_pause.hide()
        # self.stopTimer()

        self.timex += 1
        self.curveAddPoint(self.timex, random.uniform(1.5, 4.5), random.uniform(1.5, 4.5))
        self.capture_and_save_image(RunningSetting.CAM_curr_1)

    def continueDD(self):
        self.bt_continue.hide()
        self.bt_pause.show()
        self.startTimer()
        # self.myDD.continueDD()

    # 开始滴定
    def startDD(self, myDDParams):
        print(self.TAG + myDDParams.DD_Type)

    def OnImageOnChange(self, image):
        self.screen.setPixmap(image)

    # 滴定完成时
    def OnDDOnFinish(self, result):
        self.stopTimer()
        self.bt_finish.show()
        self.bt_pause.hide()

    # 回主界面
    def BackMain(self):
        self.close()

    def capture_and_save_image(self, camera_index=0):

        name = time.time()
        filename = './Auto_Ctrl/Input_dw/' + str(int(name)) + '.jpg'
        # 创建VideoCapture对象并读取摄像头画面
        cap = cv2.VideoCapture(camera_index)

        # 检查摄像头是否成功打开
        if not cap.isOpened():
            print("错误：无法打开摄像头")
            return None

        # 读取一帧画面
        ret, frame = cap.read()
        # image = Image.fromarray(frame)
        # 检查是否成功读取画面
        if not ret:
            print("错误：无法从摄像头读取画面")
            cap.release()
            return None

        # 保存画面到文件
        success = cv2.imwrite(filename, frame)

        # 检查是否成功保存
        if success:
            print(f"图像已成功保存到 {filename}")
        else:
            print(f"错误：无法保存图像到 {filename}")

        # 释放摄像头资源
        cap.release()

        return filename if success else None

    # 开始计时
    def startTimer(self):
        self.timer = QTimer(self)  # 创建一个定时器
        self.timer.timeout.connect(self.updateTime)  # 连接信号和槽
        self.start_time = 0  # 初始时间，单位是秒
        self.timer.start(1000)  # 每1000毫秒（1秒）触发一次
        print(self.TAG + "开始计时")

    # 停止计时
    def stopTimer(self):
        self.timer.stop()

    def updateTime(self):
        self.start_time += 1  # 增加1秒
        hours, remainder = divmod(self.start_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timelabel_value.setText(time_str)  # 更新标签显示的时间

    def limit_float_precision(self, value, precision):
        # 将浮点数格式化为字符串，并限制小数点后的位数
        formatted_str = "{:.{}f}".format(value, precision)
        return formatted_str

    def DrawLine(self):
        # 创建一个 Matplotlib 图表
        self.fig = Figure(figsize=(6, 4), facecolor='#525252')
        self.axes = self.fig.add_subplot(111)

        # 设定背景颜色
        self.axes.set_facecolor('#525252')

        self.plot_curve()

        # 创建一个 FigureCanvasQTAgg 实例，并将图表传递给它
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.myQLine)

        # 创建一个垂直布局，并添加 canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.myQLine.setLayout(layout)

        # self.TweenShowLineTest()
        # 设置窗口的标题和大小

        # rect = self.myQLine.geometry()
        # self.setGeometry(rect .x() , rect.y(), rect.width(), rect.height())  # x, y, width, height

    def plot_curve(self):
        # 创建数据
        # x = np.linspace(0, 10, 100)
        # y = np.sin(x)

        # 在图形上绘制曲线
        # self.axes.plot(x, y,color='blue')
        self.axes.set_title('', color='white')
        self.axes.set_xlabel('V (mL)', color='white')
        self.axes.set_ylabel('E/dE', color='white')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.grid(color='w', linewidth='1', linestyle='-.')
        # 刷新画布
        # self.canvas.draw()

    # 图表里增加 一个点
    def curveAddPoint(self, x, y_1, y_2):

        self.line_x.append(x)

        max_x = max(self.line_x)

        axis_x = np.linspace(0, max_x, 100)
        self.line_1_y.append(y_1)
        self.line_2_y.append(y_2)

        self.axes.plot(self.line_x, self.line_1_y, label='Line A', color='blue')
        self.axes.plot(self.line_x, self.line_2_y, label='Line B', color='red')

        self.canvas.draw()

    '''  
    def TweenShowLine(self):
        self.vol = self.vol+1
        print(self.vol)
        x = np.linspace(0, self.vol, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
       # 创建第一个图表

        self.axes.plot(x, y1, label='Line A',color='blue')
        self.axes.plot(x, y2, label='Line B',color='red')
        self.axes.grid(color='w',linewidth='1',linestyle='-.')
        #self.axes.legend(['Line A','Line B'])
        self.canvas.draw()
    '''


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myDD = DDParams()
    myDD.DD_Type = "氢氧化钠滴定盐酸-酚酞"
    style_file = './ElegantDark.qss'
    style_sheet = QSSLoader.read_qss_file(style_file)
    app.setStyleSheet(style_sheet)

    window = UITitrationbyReadScale(myDD)
    window.show()
    sys.exit(app.exec_())
