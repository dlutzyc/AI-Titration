#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox,QVBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from qt_start_window import Ui_UIStartWindow
from UICreate import UICreate
import cv2
from QSSLoader import QSSLoader
from RunningSetting import RunningSetting
from server.ZMQServer import ZMQServer
import time
#入口页面
class UIStart(QMainWindow, Ui_UIStartWindow):
        
    TAG="<UIStart>  "

    


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        if sys.platform.startswith('linux'):
            self.showFullScreen()
        print('UIStart---')
        self.bt_create.clicked.connect(self.createNew)
        

        # 初始化时间显示
        self.update_time_label()
        # 设置定时器每秒更新一次时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(1000)  # 每1000毫秒即1秒更新一次


        # 打开化摄像头
        #self.cap = cv2.VideoCapture(0)
        self.running = True
        self.init_timer()
        self.listCameras()
        self.OnCameralistChanged()
        #self.open_camera(True)

        self.cameralist.currentIndexChanged.connect(self.OnCameralistChanged)
        self.bt_server.clicked.connect(self.btserverOnClick)

    def btserverOnClick(self):
        ZMQServer.get_instance().showWinow()

    def update_image(self,pixmap):
        self.screen.setPixmap(pixmap)

    def run(self):
        while self.running:
            self.show_pic()

    def stop(self):
        self.running = False
        self.cap.release()

    def closeEvent(self, event):
        if ZMQServer.get_instance().running:
            ZMQServer.get_instance().stop()
# 打开相机采集视频
    def open_camera(self,shouTip):

        # 获取选择的设备名称
        self.cap = cv2.VideoCapture(RunningSetting.CAM_curr_1)
        # 检测该设备是否能打开
        flag = self.cap.open(RunningSetting.CAM_curr_1)
        print('打开摄像机：'+str(RunningSetting.CAM_curr_1))
        if flag is False:
            if shouTip:
                QMessageBox.information(self, "警告", "相机未正确连接", QMessageBox.Ok)
        else:
            # 幕布可以播放
            self.screen.setEnabled(True)
            # 打开摄像头按钮不能点击
            #self.pushButton.setEnabled(False)
            # 关闭摄像头按钮可以点击
            #self.pushButton_2.setEnabled(True)
            self.timer.start()
            print("beginning！")
    def listCameras(self):
        # 遍历摄像头索引
        for i in range(0, 10):  # 假设最多有10个摄像头
            try:
                cap = cv2.VideoCapture(i)
                if cap is not None and cap.isOpened():
                    self.cameralist.addItem('Camera {}'.format(i))
                    print('Camera {} 存在'.format(i))
                    RunningSetting.CameraIndexList.append(i)
                    if RunningSetting.CAM_curr_1==0:
                        RunningSetting.CAM_curr_1 = i#默认打开第一个摄像头
                        
                else:
                    print('Camera {} 不存在'.format(i))
                callable(cap)
                cap.release()
            except:
                cap.release()
                print('Camera {} 不存在'.format(i))
        print('默认摄像机索引为：'+str(RunningSetting.CAM_curr_1))
    
    def OnCameralistChanged(self):
        # 获取选择的设备名称
        selected_text  = self.cameralist.currentText()
        parts = selected_text.split(' ')
        if len(parts) > 1:
            number = parts[1]  # 获取下划线后面的数字
            print(f"选中的数字是: {number}")
            RunningSetting.CAM_curr_1=int(number)
            self.open_camera(True)
        else:
            print("选中的项没有包含数字")
            RunningSetting.CAM_curr_1=0
            self.open_camera(True)
            

# 播放视频画面
    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_pic)
# 显示视频图像
    def show_pic(self):
        if self.isActiveWindow()==False:
            if self.cap.isOpened():
                self.cap.release()
            return
            
        ret, img = self.cap.read()
  
        if(ret==False):
            self.open_camera(False)
            print(self.TAG+"重新激活摄像机")
        if ret:
            cur_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # 视频流的长和宽
            height, width = cur_frame.shape[:2]
            pixmap = QImage(cur_frame, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(pixmap)
            # 获取是视频流和label窗口的长宽比值的最大值，适应label窗口播放，不然显示不全
            ratio = max(width / self.screen.width(), height / self.screen.height())
            pixmap.setDevicePixelRatio(ratio)
            # 视频流置于label中间部分播放
            self.screen.setAlignment(Qt.AlignCenter)
            self.screen.setPixmap(pixmap)
#关闭相机
    def close_camera(self):
        # 关闭摄像头
        self.cap.release()
        self.timer.stop()
        print(self.TAG+"close camera")

  
#开始新滴定
    def createNew(self):
        self.cap.release()
        window = UICreate()
        window.show()
        
        

    def update_time_label(self):
        # 获取当前时间和星期信息
        current_time = QtCore.QDateTime.currentDateTime()
        formatted_time = current_time.toString("yyyy/MM/dd hh:mm:ss ddd")
        
        # 更新QLabel的文本
        self.time_label.setText(formatted_time)  # 假设你的QLabel名为label_time



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UIStart()
   
    style_file = './ElegantDark.qss'
    style_sheet = QSSLoader.read_qss_file(style_file)
    app.setStyleSheet(style_sheet)

    window.show()
    sys.exit(app.exec_())

