# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import numpy as np
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.writer.excel import ExcelWriter


def tomygray(image):
    height = image.shape[0]
    width = image.shape[1]
    gray = np.zeros((height, width, 1), np.uint8)
    for i in range(height):
        for j in range(width):
            # pixel = max(image[i,j][0], image[i,j][1], image[i,j][2])
            pixel = 0.0 * image[i, j][0] + 0.0 * image[i, j][1] + 1 * image[i, j][2]
            gray[i, j] = pixel
    return gray


def TubeIdentification(filename, num, image):
    tube = 0
    tubo_roi = [
        [image.shape[0] * 0 / 3, image.shape[0] * 1 / 3, image.shape[1] * 1 / 2,
         image.shape[1] * 1 / 2],
        [image.shape[0] * 1 / 3, image.shape[0] * 1 / 3, image.shape[1] * 2 / 3,
         image.shape[1] - 1],
        [image.shape[0] * 2 / 3, image.shape[0] * 2 / 3, image.shape[1] * 2 / 3,
         image.shape[1] - 1],
        [image.shape[0] * 2 / 3, image.shape[0] - 1, image.shape[1] * 1 / 2,
         image.shape[1] * 1 / 2],
        [image.shape[0] * 2 / 3, image.shape[0] * 2 / 3, image.shape[1] * 0 / 3,
         image.shape[1] * 1 / 3],
        [image.shape[0] * 1 / 3, image.shape[0] * 1 / 3, image.shape[1] * 0 / 3,
         image.shape[1] * 1 / 3],
        [image.shape[0] * 1 / 3, image.shape[0] * 2 / 3, image.shape[1] * 1 / 2,
         image.shape[1] * 1 / 2]]
    i = 0
    while (i < 7):
        if (Iswhite(image, int(tubo_roi[i][0]), int(tubo_roi[i][1]),
                    int(tubo_roi[i][2]), int(tubo_roi[i][3]))):
            tube = tube + pow(2, i)

        cv2.line(image, (int(tubo_roi[i][3]), int(tubo_roi[i][1])),
                 (int(tubo_roi[i][2]), int(tubo_roi[i][0])),
                 (255, 0, 0), 1)
        i += 1

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
    elif (tube == 103):
        onenumber = 9
    else:
        onenumber = -1

    cv2.imwrite(filename + '_' + str(num) + '_' + str(onenumber) + '.png', image)
    return onenumber


def Iswhite(image, row_start, row_end, col_start, col_end):
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


def digitalrec(image):
    # filename = str(image).split(".jpg", 1)[0]
    image_org = cv2.imread(image)

    height = image_org.shape[0]
    width = image_org.shape[1]

    # transe image to gray
    # image_gray = cv2.cvtColor(image_org, cv2.COLOR_RGB2GRAY)
    image_gray = tomygray(image_org)
    cv2.imwrite(image + '_gray.png', image_gray)
    # cv2.imwrite(filename + '_gray.png', image_gray)

    meanvalue = image_gray.mean()
    if meanvalue >= 200:
        hist = cv2.calcHist([image_gray], [0], None, [256], [0, 256])
        # plt.hist(hist.ravel(), 256, [0,256])
        # plt.savefig(filename + "_hist.png")
        # plt.show()
        min_val, max_val, min_index, max_index = cv2.minMaxLoc(hist)
        ret, image_bin = cv2.threshold(image_gray, int(max_index[1]) - 7, 255,
                                       cv2.THRESH_BINARY)
    else:
        mean, stddev = cv2.meanStdDev(image_gray)
        ret, image_bin = cv2.threshold(image_gray, meanvalue + 65, 255,
                                       cv2.THRESH_BINARY)

    # image_bin = cv2.adaptiveThreshold(image_gray, 255,
    #                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                  cv2.THRESH_BINARY, 11,
    #                                  0)

    x, y, w, h = cv2.boundingRect(image_bin)
    image_bin = image_bin[max(y - 5, 0): h + 10, max(x - 5, 0): w + 10]
    cv2.imwrite(image + '_bin.png', image_bin)

    # split number and identify it
    num = 0
    result = ''
    while True:
        if num < 3:
            roi = image_bin[0: height, int(width / 3 * num):
                                       int(width / 3 * (num + 1))]
            onenumber = TubeIdentification(image, num, roi)
            if onenumber == -1:
                result += "0"
            else:
                result += str(onenumber)
            num += 1
        else:
            break
    print("picture of %s detect result is %s" % (image, result))
    return result


if __name__ == '__main__':
    text = digitalrec("Input/PH.png")
    print(text)
