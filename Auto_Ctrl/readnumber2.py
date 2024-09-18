import cv2
import numpy as np

# 假设TRAINDATANUM, TRAINPATH, NORMWIDTH, NORMHEIGHT, tube_num, tube（一个包含图像的列表）已经被定义  

# 初始化traindata和trainlabel列表  
traindata = []
trainlabel = []

# 读取并处理训练数据  
for i in range(TRAINDATANUM):
    trainfile = f"{TRAINPATH}\\{i}.jpg"
    img = cv2.imread(trainfile, cv2.IMREAD_GRAYSCALE)
    _, img_binary = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    img_resized = cv2.resize(img_binary, (NORMWIDTH, NORMHEIGHT))
    # OpenCV的机器学习模型通常期望二维浮点数数组，所以这里我们直接将其转换为浮点数
    traindata.append(img_resized.reshape((-1, 1)).astype(np.float32))
    trainlabel.append(i)

# 转换为NumPy数组（如果需要）  
traindata = np.vstack(traindata)
trainlabel = np.array(trainlabel)

# 使用KNN分类器  
K = 1
knn = cv2.ml.KNearest_create()
knn.train(np.float32(traindata), cv2.ml.ROW_SAMPLE, trainlabel)

# 对tube中的图像进行预测  
for i in range(tube_num):
    img = tube[i]
    img_resized = cv2.resize(img, (NORMWIDTH, NORMHEIGHT))
    # OpenCV的机器学习模型期望二维浮点数数组
    sample = img_resized.reshape((-1, 1)).astype(np.float32)
    # 使用KNN进行预测
    _, r = knn.predict(sample)
    print(r[0])