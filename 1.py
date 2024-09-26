#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: 1.py
Author: Zinc Zou
Email: zincou@163.com
Date: 2024/9/26
Copyright: 慕乐网络科技(大连）有限公司
        www.mools.net
        moolsnet@126.com
Description: 
"""
import torch


def print_hi(name):
    print(torch.cuda.is_available())
    device = torch.device("cuda:0")



if __name__ == '__main__':
    print_hi('1')
