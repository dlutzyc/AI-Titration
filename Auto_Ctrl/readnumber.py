#!/usr/bin/python
# -*- coding:utf-8 -*-
import cv2
import time



class readnumber:
    def __init__(self, videoSourceIndex=0, types=1, *args, **kwargs):
        # 输入量有两个
        # videoSourceIndex 摄像头编号 (int,默认为0)
        # types 所读取数码管屏幕的模式 (暂时设计为布尔值，但是以int的方式呈现）
        # 如示例中白底黑字的数码管为1，黑底白字（或其他亮字）为0(主要区别为灰度图像是否反色)
        super().__init__()
        self.filename = self.capture_and_save_image(videoSourceIndex)  # 获取照片
        # filename = 'Input/PH1.jpg'  # 测试时使用的指定照片作为输入
        self.numberlist = self.read_number(self.filename, types)
        number_str = ''.join(map(str, self.numberlist))
        # 然后将字符串转换回整数
        try:
            self.decimal_number = int(number_str)
        except:
            self.decimal_number = 0
        print(self.decimal_number)
        # 输出量为所读取的数字，暂时未写输出方法（我不太清楚class.init怎么写输出）

    def capture_and_save_image(self, camera_index=0):

        name = time.time()
        filename = './Auto_Ctrl/Input_dw/PH' + str(int(name)) + '.jpg'
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

    # 将彩色图像转换成灰度图像并进行反转
    def invert_color(self, fname, types):
        # 打开彩色原始图像
        img_color = cv2.imread(fname)
        # 将彩色图像转换成灰度图像
        # 注意参数2：OpenCV中彩色色彩空间是BGR，转换成灰度色彩空间GRAY
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        # 获取灰度图像宽、高、通道数
        # height_gray, width_gray = img_gray.shape
        height_gray, width_gray = img_gray.shape[:2]
        # 打印彩色图像的宽、高、通道数
        # print("gray:width[%d],height[%d]" % (width_gray, height_gray))

        # 灰度图像反色,仅当types为True时执行
        # 创建空白数组
        if types:
            for row in range(height_gray):
                for col in range(width_gray):
                    img_gray[row][col] = 255 - img_gray[row][col]


        # 显示和保存反色后灰度图像
        # cv2.imshow('dst_gray', img_gray)
        cv2.imwrite('Input/dstPH1.jpg', img_gray)
        return img_gray

    # 定义判断区域是否全为白色的函数
    def is_all_white(self, image, row_start, row_end, col_start, col_end):
        white_num = 0
        j = row_start
        i = col_start

        while (j <= row_end):
            while (i <= col_end):
                if (image[j][i] == 255):
                    white_num += 1
                i += 1
            j += 1
            i = col_start
        # print('white num is',white_num)
        if (white_num >= 5):
            return True
        else:
            return False

    # 定义穿线法识别数字的函数
    def tube_identification(self, inputmat):
        tube = 0
        tubo_roi = [
            [inputmat.shape[0] * 0 / 3, inputmat.shape[0] * 1 / 3, inputmat.shape[1] * 1 / 2,
             inputmat.shape[1] * 1 / 2],
            # a
            [inputmat.shape[0] * 1 / 3, inputmat.shape[0] * 1 / 3, inputmat.shape[1] * 2 / 3, inputmat.shape[1] - 1],
            # b
            [inputmat.shape[0] * 2 / 3, inputmat.shape[0] * 2 / 3, inputmat.shape[1] * 2 / 3, inputmat.shape[1] - 1],
            # c
            [inputmat.shape[0] * 2 / 3, inputmat.shape[0] - 1, inputmat.shape[1] * 1 / 2, inputmat.shape[1] * 1 / 2],
            # d
            [inputmat.shape[0] * 2 / 3, inputmat.shape[0] * 2 / 3, inputmat.shape[1] * 0 / 3,
             inputmat.shape[1] * 1 / 3],
            # e
            [inputmat.shape[0] * 1 / 3, inputmat.shape[0] * 1 / 3, inputmat.shape[1] * 0 / 3,
             inputmat.shape[1] * 1 / 3],
            # f
            [inputmat.shape[0] * 1 / 3, inputmat.shape[0] * 2 / 3, inputmat.shape[1] * 1 / 2, inputmat.shape[1] * 1 / 2]
            # g
        ]
        i = 0
        while (i < 7):
            if (
                    self.is_all_white(inputmat, int(tubo_roi[i][0]), int(tubo_roi[i][1]), int(tubo_roi[i][2]),
                                      int(tubo_roi[i][3]))):
                tube = tube + pow(2, i)

            cv2.line(inputmat, (int(tubo_roi[i][3]), int(tubo_roi[i][1])),
                     (int(tubo_roi[i][2]), int(tubo_roi[i][0])),
                     (255, 0, 0), 1)
            i += 1
        if (inputmat.shape[0] / inputmat.shape[1] > 2):  # 1 is special, which is much narrower than others
            tube = 6
        if (tube == 63):
            onenumber = 0
        elif (tube == 6):
            onenumber = 1
        elif (tube == 91):
            onenumber = 2
        elif (tube == 79):
            onenumber = 3
        elif (tube == 102 or tube == 110):
            # 110是因为有干扰情况
            onenumber = 4
        elif (tube == 109):
            onenumber = 5
        elif (tube == 125):
            onenumber = 6
        elif (tube == 7):
            onenumber = 7
        elif (tube == 127):
            onenumber = 8
        elif (tube == 111):
            onenumber = 9
        else:
            print("error tube = ", tube)
            onenumber = -1
            # 错误数字
        return onenumber

    def read_number(self, filename, types):
        # 原图
        image = cv2.imread(filename, cv2.IMREAD_COLOR)
        # cv2.imshow("image", image)

        # 灰度图处理
        refile = self.invert_color(filename, types)
        # image_gry = cv2.imread(refile, cv2.IMREAD_GRAYSCALE)
        if refile is None:
            print("not read")
            exit()
        # cv2.imshow("image_gry", refile)

        # 二值化

        # _, image_bin = cv2.threshold(refile, 80, 255, cv2.THRESH_BINARY)
        _, image_bin = cv2.threshold(refile, 0, 255, cv2.THRESH_OTSU);
        # cv2.imshow("image_bin", image_bin)

        # 进行膨胀处理
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        image_dil = cv2.dilate(image_bin, element)
        # cv2.imshow("image_dil", image_dil)

        # 轮廓寻找
        contours_out, hierarchy = cv2.findContours(image_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # cv2.drawContours(image_bin,contours,-1,(0,255,0),2)
        num_location = [cv2.boundingRect(contour) for contour in contours_out]
        num_location.sort(key=lambda x: x[0])
        inmage_with_contours = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(inmage_with_contours, contours_out, -1, (0, 225, 0), 2)

        # cv2.imshow("Contours", inmage_with_contours)

        # 存储通过穿线法识别的数字
        detected_numbers = []

        # 遍历每个数字区域
        for i in range(len(num_location)):
            x, y, w, h = num_location[i]
            num_region = image_dil[y:y + h, x:x + w]  # 提取数字区域
            if h > w and 150 > h > 100:
                # 调用穿线法识别数字
                detected_number = self.tube_identification(num_region)
                detected_numbers.append(detected_number)
                # if detected_number >= 0 :
                # 显示数字区域
                # cv2.imshow(str(i), num_region)
                # print(str(i), detected_number)
                # print(h,w)

        # 清除所有的错误数字

        # 输出识别到的数字
        # print("Detected Numbers:", detected_numbers)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return detected_numbers


if __name__ == '__main__':
    # videoSourceIndex = 0  # 摄像机编号，请根据自己的情况调整
    readnumber()
