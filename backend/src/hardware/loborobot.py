#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# src/hardware/loborobot.py
# 底层硬件驱动：PCA9685 PWM 控制器 + LOBOROBOT 四轮麦克纳姆轮底盘
# 以及高层异步 Robot 单例接口
#
# 原始来源：backend/LOBOROBOT.py
# 仅在树莓派环境（smbus + RPi.GPIO 可用）下可正常实例化

import time
import math
import asyncio
from typing import Final

import smbus
import RPi.GPIO as GPIO

from src.logger import info


Dir = [
    'forward',
    'backward',
]


# ---------------------------------------------------------------------------
# PCA9685 — I2C PWM 驱动芯片
# ---------------------------------------------------------------------------

class PCA9685:

    # Registers/etc.
    __SUBADR1   = 0x02
    __SUBADR2   = 0x03
    __SUBADR3   = 0x04
    __MODE1     = 0x00
    __PRESCALE  = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L  = 0xFA
    __ALLLED_ON_H  = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address: int, debug: bool = False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug:
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg: int, value: int) -> None:
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg: int) -> int:
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq: int) -> None:
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if self.debug:
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if self.debug:
            print("Final pre-scale: %d" % prescale)
        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10   # sleep
        self.write(self.__MODE1, newmode)
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel: int, on: int, off: int) -> None:
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L  + 4 * channel, on  & 0xFF)
        self.write(self.__LED0_ON_H  + 4 * channel, on  >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if self.debug:
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setDutycycle(self, channel: int, pulse: float) -> None:
        self.setPWM(channel, 0, int(pulse * (4096 / 100)))

    def setLevel(self, channel: int, value: int) -> None:
        if value == 1:
            self.setPWM(channel, 0, 4095)
        else:
            self.setPWM(channel, 0, 0)


# ---------------------------------------------------------------------------
# LOBOROBOT — 四轮麦克纳姆轮底盘底层控制
# ---------------------------------------------------------------------------

class LOBOROBOT:
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 2
        self.AIN2 = 1

        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

        self.PWMC = 6
        self.CIN2 = 7
        self.CIN1 = 8

        self.PWMD = 11
        self.DIN1 = 25
        self.DIN2 = 24

        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DIN1, GPIO.OUT)
        GPIO.setup(self.DIN2, GPIO.OUT)

    def MotorRun(self, motor: int, index: str, speed: int) -> None:
        if speed > 100:
            return
        if motor == 0:
            self.pwm.setDutycycle(self.PWMA, speed)
            if index == Dir[0]:
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            else:
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
        elif motor == 1:
            self.pwm.setDutycycle(self.PWMB, speed)
            if index == Dir[0]:
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)
            else:
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
        elif motor == 2:
            self.pwm.setDutycycle(self.PWMC, speed)
            if index == Dir[0]:
                self.pwm.setLevel(self.CIN1, 1)
                self.pwm.setLevel(self.CIN2, 0)
            else:
                self.pwm.setLevel(self.CIN1, 0)
                self.pwm.setLevel(self.CIN2, 1)
        elif motor == 3:
            self.pwm.setDutycycle(self.PWMD, speed)
            if index == Dir[0]:
                GPIO.output(self.DIN1, 0)
                GPIO.output(self.DIN2, 1)
            else:
                GPIO.output(self.DIN1, 1)
                GPIO.output(self.DIN2, 0)

    def MotorStop(self, motor: int) -> None:
        if motor == 0:
            self.pwm.setDutycycle(self.PWMA, 0)
        elif motor == 1:
            self.pwm.setDutycycle(self.PWMB, 0)
        elif motor == 2:
            self.pwm.setDutycycle(self.PWMC, 0)
        elif motor == 3:
            self.pwm.setDutycycle(self.PWMD, 0)

    # 前进
    def t_up(self, speed: int) -> None:
        self.MotorRun(0, 'forward', speed)
        self.MotorRun(1, 'forward', speed)
        self.MotorRun(2, 'forward', speed)
        self.MotorRun(3, 'forward', speed)

    # 后退
    def t_down(self, speed: int) -> None:
        self.MotorRun(0, 'backward', speed)
        self.MotorRun(1, 'backward', speed)
        self.MotorRun(2, 'backward', speed)
        self.MotorRun(3, 'backward', speed)

    # 左移（横向）
    def moveLeft(self, speed: int) -> None:
        self.MotorRun(0, 'backward', speed)
        self.MotorRun(1, 'forward',  speed)
        self.MotorRun(2, 'forward',  speed)
        self.MotorRun(3, 'backward', speed)

    # 右移（横向）
    def moveRight(self, speed: int) -> None:
        self.MotorRun(0, 'forward',  speed)
        self.MotorRun(1, 'backward', speed)
        self.MotorRun(2, 'backward', speed)
        self.MotorRun(3, 'forward',  speed)

    # 原地左转
    def turnLeft(self, speed: int) -> None:
        self.MotorRun(0, 'backward', speed)
        self.MotorRun(1, 'forward',  speed)
        self.MotorRun(2, 'backward', speed)
        self.MotorRun(3, 'forward',  speed)

    # 原地右转
    def turnRight(self, speed: int) -> None:
        self.MotorRun(0, 'forward',  speed)
        self.MotorRun(1, 'backward', speed)
        self.MotorRun(2, 'forward',  speed)
        self.MotorRun(3, 'backward', speed)

    # 前左斜
    def forward_Left(self, speed: int) -> None:
        self.MotorStop(0)
        self.MotorRun(1, 'forward', speed)
        self.MotorRun(2, 'forward', speed)
        self.MotorStop(3)

    # 前右斜
    def forward_Right(self, speed: int) -> None:
        self.MotorRun(0, 'forward', speed)
        self.MotorStop(1)
        self.MotorStop(2)
        self.MotorRun(3, 'forward', speed)

    # 后左斜
    def backward_Left(self, speed: int) -> None:
        self.MotorRun(0, 'backward', speed)
        self.MotorStop(1)
        self.MotorStop(2)
        self.MotorRun(3, 'backward', speed)

    # 后右斜
    def backward_Right(self, speed: int) -> None:
        self.MotorStop(0)
        self.MotorRun(1, 'backward', speed)
        self.MotorRun(2, 'backward', speed)
        self.MotorStop(3)

    # 全停
    def t_stop(self) -> None:
        self.MotorStop(0)
        self.MotorStop(1)
        self.MotorStop(2)
        self.MotorStop(3)

    # 设置舵机脉冲宽度
    def set_servo_pulse(self, channel: int, pulse: int) -> None:
        pulse_length = 1000000
        pulse_length //= 60
        pulse_length //= 4096
        pulse *= 1000
        pulse //= pulse_length
        self.pwm.setPWM(channel, 0, pulse)

    # 设置舵机角度
    def set_servo_angle(self, channel: int, angle: float) -> None:
        angle = 4096 * ((angle * 11) + 500) / 20000
        self.pwm.setPWM(channel, 0, int(angle))


# ---------------------------------------------------------------------------
# Robot — 高层异步单例接口
# ---------------------------------------------------------------------------

class _Robot:
    """
    四轮麦克纳姆轮机器人高层异步控制接口（单例）。

    通过 ``Robot`` 全局对象访问，不要直接实例化本类。

    前进/后退固定使用 FORWARD_SPEED，旋转固定使用 ROTATE_SPEED，
    运行时间由对应实测速度常数自动计算，无需外部传入速度。

    重新标定步骤：
      1. 跑 bot.t_up(FORWARD_SPEED) 持续 T 秒，量出距离 d
         → V_FORWARD = d / T
      2. 跑 bot.turnLeft(ROTATE_SPEED) 持续 T 秒，数出总转角 θ°
         → V_ROTATE = θ / T
    """

    # ------------------------------------------------------------------
    # 固定速度常数（百分比 0–100，禁止在运行时修改）
    # ------------------------------------------------------------------
    FORWARD_SPEED: Final[int] = 30   # 前进/后退专用速度
    ROTATE_SPEED:  Final[int] = 30   # 旋转专用速度

    # ------------------------------------------------------------------
    # 实测物理参数（标定值，与上方速度常数严格对应）
    # 实测：FORWARD_SPEED=30，跑 3s，走 0.645m → 0.645 / 3 = 0.215 m/s
    # 实测：ROTATE_SPEED=30，跑 10s，转 960°   → 960  / 10 = 96.0 deg/s
    # ------------------------------------------------------------------
    V_FORWARD: Final[float] = 0.215  # 单位：m/s
    V_ROTATE:  Final[float] = 96.0   # 单位：deg/s

    _instance: "_Robot | None" = None

    def __new__(cls) -> "_Robot":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bot = LOBOROBOT()
        return cls._instance

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _linear_delay(self, distance: float) -> float:
        """根据固定前进速度和距离计算运行时间（秒）。"""
        if self.V_FORWARD <= 0:
            return 0.0
        return distance / self.V_FORWARD

    def _angular_delay(self, degree: float) -> float:
        """根据固定旋转速度和角度计算运行时间（秒）。"""
        if self.V_ROTATE <= 0:
            return 0.0
        return degree / self.V_ROTATE

    # ------------------------------------------------------------------
    # 运动指令（异步）
    # ------------------------------------------------------------------

    async def forward(self, distance: float) -> None:
        """前进指定距离（米），使用固定速度 FORWARD_SPEED。"""
        delay = self._linear_delay(distance)
        info(f"[Robot] forward | distance={distance:.3f}m | speed={self.FORWARD_SPEED} | duration={delay:.3f}s")
        self._bot.t_up(self.FORWARD_SPEED)
        await asyncio.sleep(delay)
        self._bot.t_stop()
        info(f"[Robot] forward done | stopped after {delay:.3f}s")

    async def backward(self, distance: float) -> None:
        """后退指定距离（米），使用固定速度 FORWARD_SPEED。"""
        delay = self._linear_delay(distance)
        info(f"[Robot] backward | distance={distance:.3f}m | speed={self.FORWARD_SPEED} | duration={delay:.3f}s")
        self._bot.t_down(self.FORWARD_SPEED)
        await asyncio.sleep(delay)
        self._bot.t_stop()
        info(f"[Robot] backward done | stopped after {delay:.3f}s")

    async def turn_left(self, degree: int = 90) -> None:
        """原地左转指定角度（度），默认 90°，使用固定速度 ROTATE_SPEED。"""
        delay = self._angular_delay(degree)
        info(f"[Robot] turn_left | degree={degree}° | speed={self.ROTATE_SPEED} | duration={delay:.3f}s")
        self._bot.turnLeft(self.ROTATE_SPEED)
        await asyncio.sleep(delay)
        self._bot.t_stop()
        info(f"[Robot] turn_left done | stopped after {delay:.3f}s")

    async def turn_right(self, degree: int = 90) -> None:
        """原地右转指定角度（度），默认 90°，使用固定速度 ROTATE_SPEED。"""
        delay = self._angular_delay(degree)
        info(f"[Robot] turn_right | degree={degree}° | speed={self.ROTATE_SPEED} | duration={delay:.3f}s")
        self._bot.turnRight(self.ROTATE_SPEED)
        await asyncio.sleep(delay)
        self._bot.t_stop()
        info(f"[Robot] turn_right done | stopped after {delay:.3f}s")


# 全局单例
Robot = _Robot()


__all__ = ["LOBOROBOT", "Robot"]
