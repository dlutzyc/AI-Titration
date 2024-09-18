import RPi.GPIO as GPIO
import time

# 设置GPIO模式为BCM（Broadcom SOC channel）
GPIO.setmode(GPIO.BCM)

# 选择一个支持PWM的GPIO引脚（例如，BCM编号的18）
PWM_PIN = 18

# 初始化PWM，频率为100Hz
pwm = GPIO.PWM(PWM_PIN, 100)

# 开始PWM输出，占空比设置为0（即关闭）
pwm.start(0)

try:
    # 逐渐增加占空比到100（即完全打开），然后逐渐减小到0
    for dc in range(0, 101, 5):  # 0到100，步长为5
        pwm.ChangeDutyCycle(dc)
        time.sleep(0.1)  # 等待0.1秒

    for dc in range(100, -1, -5):  # 100到0，步长为-5
        pwm.ChangeDutyCycle(dc)
        time.sleep(0.1)  # 等待0.1秒

except KeyboardInterrupt:
    # 如果用户按下Ctrl+C，则清理并退出
    pwm.stop()
    GPIO.cleanup()