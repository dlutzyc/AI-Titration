import RPi.GPIO as GPIO
import time

class Stir:
    # 现在有一个问题是我不确定这个程序和电机控制程序会不会打架，不过我设计的在不同的引脚
    def __init__(self, dc=100, *args, **kwargs):
        # 输入量有一个
        # dc 转速 (0~100之间的float)
        # 我的想法是弄一个滑动条
        super().__init__()
        # 设置GPIO模式为BCM（Broadcom SOC channel）或者BOARD（物理引脚编号）
        GPIO.setmode(GPIO.BCM)  # 或者使用GPIO.BOARD
        # 选择一个支持PWM的GPIO引脚（例如，BCM编号的18）
        self.PWM_PIN = 18
        # 设置GPIO引脚为输出模式
        GPIO.setup(self.PWM_PIN, GPIO.OUT)
        # 初始化PWM，频率为100Hz
        self.pwm = GPIO.PWM(self.PWM_PIN, 100)
        # 开始PWM输出，占空比设置为0（即关闭）
        self.pwm.start(0)
        self.Change_Stir(dc)


    def Change_Stir(self, dc):
        try:
            while True:
                user_input = input("请输入一个数字：")
                if user_input:
                    if float(user_input) < 80:
                        self.pwm.ChangeDutyCycle(100)
                        time.sleep(0.5)
                    # 按照输入值调整占空比（模拟电压大小）默认值100（即完全打开）
                    self.pwm.ChangeDutyCycle(float(user_input))
                time.sleep(0.1)  # 等待0.1秒

        finally:
            # 如果用户按下Ctrl+C，则清理并退出
            # 或者设定某个条件，比如滴定程序返回停止信号
            self.pwm.ChangeDutyCycle(100)
            time.sleep(0.1)
            self.pwm.stop()
            GPIO.cleanup()


if __name__ == '__main__':
    # videoSourceIndex = 0  # 摄像机编号，请根据自己的情况调整
    Stir()