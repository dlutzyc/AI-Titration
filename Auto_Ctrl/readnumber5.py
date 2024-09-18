import cv2
import numpy as np
import imutils


def nothing(x):
    pass


img = cv2.imread('test.jpg')
image = imutils.resize(img, height=300)
image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 创建窗口
cv2.namedWindow('Canny')

# 创建滑动条，分别对应Canny的两个阈值
cv2.createTrackbar('threshold1', 'Canny', 0, 255, nothing)
cv2.createTrackbar('threshold2', 'Canny', 0, 255, nothing)
# cv2.createTrackbar('threshold3', 'Canny', 0, 255, nothing)

while (1):

    # 返回当前阈值
    threshold1 = cv2.getTrackbarPos('threshold1', 'Canny')
    threshold2 = cv2.getTrackbarPos('threshold2', 'Canny')
    # threshold3 = cv2.getTrackbarPos('threshold3', 'Canny')
    _, img_output = cv2.threshold(img_gray, threshold1, threshold2, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 显示图片
    cv2.imshow('original', img)
    cv2.imshow('Canny', img_output)

    # 空格跳出
    if cv2.waitKey(1) == ord(' '):
        break

    # 摧毁所有窗口
cv2.destroyAllWindows()

if result.shape[1] < 100:  # 如果宽度过小，则为1或"."
    # 计算白色像素占比
    total_pixels = result.shape[0] * result.shape[1]
    white_pixels = np.count_nonzero(result == 255)
    white_pixel_ratio = white_pixels / total_pixels
    if 0 < white_pixel_ratio < 0.33:
        number = 1
        digits.append(number)

    else:
        if white_pixel_ratio > 0.66 or white_pixel_ratio == 0:
            number = '.'
            digits.append(number)

