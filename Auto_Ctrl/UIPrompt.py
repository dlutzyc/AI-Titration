#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import QApplication, QDialog,QTextEdit,QVBoxLayout
from PyQt5 import QtCore,QtWidgets
from qt_prompt_window import Ui_Prompt
import sys


class Prompt(QDialog,Ui_Prompt):

        


        def __init__(self):
                super().__init__()
                self.setupUi(self)
                self.bt_enter.clicked.connect(self.enterOnClick)
                self.bt_cancel.clicked.connect(self.cancelOnClick)
                # 隐藏边框
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint |QtCore.Qt.WindowStaysOnTopHint)
                self.showFullScreen()
                # 可选：如果还想隐藏标题栏，取消下面的注释
                # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        def setContentStr(self,content):
                self.contentLabel.setText(content)

        @staticmethod
        def Show(content,entercb,cancelcb):
                print(content)
                myprompt = Prompt()
                myprompt.setContentStr(content)
                myprompt.bt_enter.clicked.connect(entercb)
                myprompt.bt_cancel.clicked.connect(cancelcb)

                
                myprompt.show()
                myprompt.exec_()
                
        def enterOnClick(self):
                self.close()
        def cancelOnClick(self):
                self.close()       
                