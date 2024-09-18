from PIL import Image
import pytesseract
import cv2

# 安装Tesseract OCR引擎并配置路径
# 下载Tesseract-OCR引擎：https://github.com/tesseract-ocr/tesseract
# 安装并配置环境变量

# 初始化Tesseract OCR引擎
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 修改为你的Tesseract路径

# 打开图片
image = Image.open('digits.png')  # 修改为你的数码管图片文件路径

# 将图片转换为灰度图，并二值化
gray = image.convert('L')
binary = gray.point(lambda x: 0 if x < 140 else 255, '1')

# 使用Tesseract OCR来识别数字
text = pytesseract.image_to_string(binary, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

# 打印识别的结果
print(text)
