# -*- coding: utf-8 -*-

import os
import time
from PIL import Image,ImageChops,ImageEnhance
def image_reversal(img,savefilepath,save_filename):
    """ 图像翻转"""
    lr=img.transpose(Image.FLIP_LEFT_RIGHT) # 左右翻转
    ud=img.transpose(Image.FLIP_TOP_BOTTOM) # 上下翻转
    lr.save(savefilepath+save_filename)
    ud.save(savefilepath+save_filename)


def image_rotation(img,savefilepath,save_filename):
    """图像旋转"""
    out1=img.rotate(40) # 旋转20度
    out2=img.rotate(30) # 旋转30度
    out1.save(savefilepath+save_filename)
    out2.save(savefilepath+save_filename)


def image_translation(img,savefilepath,save_filename):
    """图像平移"""
    out3=ImageChops.offset(img,20,0) # 只沿X轴平移
    out4=ImageChops.offset(img,0,20) # 只沿y轴平移
    out3.save(savefilepath+save_filename)
    out4.save(savefilepath+save_filename)


def image_brightness(img,savefilepath,save_filename):
    """亮度调整"""
    bri=ImageEnhance.Brightness(img)
    bri_img1=bri.enhance(0.8) # 小于1为减弱
    bri_img2=bri.enhance(1.2) # 大于1为增强
    bri_img1.save(savefilepath+save_filename)
    bri_img2.save(savefilepath+save_filename)


def image_chroma(img,savefilepath,save_filename):
    """色度调整"""
    col = ImageEnhance.Color(img)
    col_img1 = col.enhance(0.7) # 色度减弱
    col_img2 = col.enhance(1.3) # 色度增强
    col_img1.save(savefilepath+save_filename)
    col_img2.save(savefilepath+save_filename)


def image_contrast(img,savefilepath,save_filename):
    """对比度调整"""
    con=ImageEnhance.Contrast(img)
    con_img1=con.enhance(0.7) # 对比度减弱
    con_img2=con.enhance(1.3) # 对比度增强
    con_img1.save(savefilepath+save_filename)
    con_img2.save(savefilepath+save_filename)



def image_sharpness(img,savefilepath,save_filename):
    """锐度调整"""
    sha = ImageEnhance.Sharpness(img)
    sha_img1 = sha.enhance(0.5) # 锐度减弱
    sha_img2 = sha.enhance(1.5) # 锐度增强
    sha_img1.save(savefilepath+save_filename)
    sha_img2.save(savefilepath+save_filename)


# 定义扩充图片函数
def image_expansion(filepath,savefilepath,save_prefix):
    """
    :param filepath: 图片路径
    :param savefilepath: 扩充保存图片路径
    :param save_prefix: 图片前缀
    :return: 图片扩充数据集
    """
    i = 1
    for parent, dirnames, filenames in os.walk(filepath):
        for filename in filenames:
            image_path=filepath+filename
            print('正在扩充图片：%s' %filename)
            try:
                img=Image.open(image_path)
                if img.mode == "P":
                    img = img.convert('RGB')
                image_reversal(img,savefilepath,save_filename=save_prefix + str(i) + '.jpg')
                i += 1
                image_rotation(img,savefilepath,save_filename=save_prefix+str(i)+'.jpg')
                i += 1
                image_translation(img,savefilepath,save_filename=save_prefix+str(i)+'.jpg')
                i += 1
                # image_chroma(img,savefilepath,save_filename=save_prefix+str(i)+'.jpg')
                # i += 1
                # image_contrast(img,savefilepath,save_filename=save_prefix+str(i)+'.jpg')
                # i += 1
                # image_sharpness(img,savefilepath,save_filename=save_prefix+str(i)+'.jpg')
                # i += 1
            except Exception as e:
                print(e)
                pass



if __name__ == '__main__':
    # 设置图片路径
    filepath = 'C:/Picture_Train/ju/'

    # 设置扩充保存图片路径
    savefilepath ='C:/Picture_Train/new_ju/'

    # 设置前缀图片名称
    save_prefix='ticket_0_'

    time1 = time.time()
    image_expansion(filepath, savefilepath,save_prefix)
    time2 = time.time()
    print('总共耗时：' + str(time2 - time1) + 's')
