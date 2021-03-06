"""
通过实时截屏对比左侧8个指纹切片和右侧指纹图匹配度的方法
"""
from winsound import Beep
from PIL import ImageGrab
import keyboard
import threading
import time
import os
import configparser
import cv2
import numpy as np


class FingerprinterHack:
    def __init__(self, mode="1"):
        effest = 3
        self.__xOy = (
            (481 + effest, 277 + effest, 587 - effest, 383 - effest),
            (625 + effest, 277 + effest, 731 - effest, 383 - effest),
            (481 + effest, 421 + effest, 587 - effest, 527 - effest),
            (625 + effest, 421 + effest, 731 - effest, 527 - effest),
            (481 + effest, 565 + effest, 587 - effest, 671 - effest),
            (625 + effest, 565 + effest, 731 - effest, 671 - effest),
            (481 + effest, 709 + effest, 587 - effest, 815 - effest),
            (625 + effest, 709 + effest, 731 - effest, 815 - effest),
        )
        self.__mode = mode
        self.__onoff = False
        self.__confirmationImg = "confirmation.png"
        self.__key_press_delay = 0.05
        self.__key_release_delay = 0.05
        self.__save_screenshot = False
        self.__currentGroupIndex = 99
        self.__pos = list()
        self.__threadPool = list()

    @property
    def key_press_delay(self):
        return self.__key_press_delay

    @key_press_delay.setter
    def key_press_delay(self, value: float):
        self.__key_press_delay = value / 1000

    @property
    def key_release_delay(self):
        return self.__key_release_delay

    @key_release_delay.setter
    def key_release_delay(self, value: float):
        self.__key_release_delay = value / 1000

    @property
    def confirmationImg(self):
        return self.__confirmationImg

    @confirmationImg.setter
    def confirmationImg(self, imgPath: str):
        self.__confirmationImg = imgPath

    @property
    def save_screenshot(self):
        return self.__save_screenshot

    @save_screenshot.setter
    def save_screenshot(self, status: bool):
        self.__save_screenshot = status

    def onoff(self, status: bool):
        """设置开关状态\n
        status bool: True开启|False关闭\n
        """
        self.__onoff = status
        if status is True:
            Beep(1600, 600)
        else:
            Beep(600, 600)

    def main_thread_cv2(self):
        """主线程cv2方法"""
        while True:
            if self.__onoff is False:
                time.sleep(0.1)
                continue
            elif self.mathing_confirmation() < 0.1:
                self.__currentGroupIndex = 0
                im = ImageGrab.grab()
                if self.__save_screenshot is True:
                    im.save(f"screenshot{self.__currentGroupIndex}.png")
                self.cv2screen(cv2.cvtColor(np.asanyarray(im), cv2.COLOR_RGB2GRAY))
                for pos in self.__pos:
                    dis = pos - self.__currentGroupIndex
                    self.send_key("s", dis // 2)
                    self.send_key("d", dis % 2)
                    self.send_key("enter", 1)
                    self.send_key("tab", 1)
                    self.__currentGroupIndex = pos
                if self.__mode == "1":
                    self.onoff(False)
                else:
                    time.sleep(4.15)

    def send_key(self, key, count: int = 1):
        """发送键盘按键指令\n
        key str: 键盘名\n
        count int: 重复次数\n
        """
        for _ in range(count):
            keyboard.press(key)
            time.sleep(self.__key_press_delay)
            keyboard.release(key)
            time.sleep(self.__key_release_delay)

    def mathing_fingerprint(self, im_src, fingerprint, index: int):
        """匹配指纹获取格子索引\n
        im_src: 屏幕截图序列\n
        fingerprint: 指纹图序列\n
        index int: 格子位置索引\n
        """
        template_src = im_src[self.__xOy[index][1] : self.__xOy[index][3], self.__xOy[index][0] : self.__xOy[index][2]]
        template = cv2.resize(template_src, [129, 129])
        minV = cv2.minMaxLoc(cv2.matchTemplate(fingerprint, template, cv2.TM_SQDIFF_NORMED))[0]
        if minV < 0.3:
            self.__pos.append(index)

    def mathing_confirmation(self):
        """当前截屏判断"""
        templ = cv2.imread(self.__confirmationImg, 0)
        im = cv2.cvtColor(np.asanyarray(ImageGrab.grab()), cv2.COLOR_RGB2GRAY)[133:163, 470:515]
        res = cv2.matchTemplate(im, templ, cv2.TM_SQDIFF_NORMED)
        return cv2.minMaxLoc(res)[0]

    def cv2screen(self, screenshot):
        """cv2多线程扫描\n
        screenshot numpy.array: 序列化的图片\n
        """
        fingerprint = screenshot[130:690, 950:1340]
        self.__pos = list()
        for i in range(8):
            th = threading.Thread(
                target=self.mathing_fingerprint,
                args=(
                    screenshot,
                    fingerprint,
                    i,
                ),
            )
            self.__threadPool.append(th)
            th.start()
        for th in self.__threadPool:
            th.join()
        self.__pos.sort()

    def status_thread(self):
        """开关控制线程"""
        keyboard.add_hotkey("f", self.onoff, args=(True,))  # 开启
        keyboard.add_hotkey("q", self.onoff, args=(False,))  # 关闭

    def run(self):
        threading.Thread(target=self.status_thread).start()
        threading.Thread(target=self.main_thread_cv2).start()


def get_input():
    return input("\r选择模式:[1]手动触发执行扫描 [2]自动实时扫描 (输入1或2回车)\n输入:").strip()


def main():
    while True:
        mode = get_input()
        if mode in ("1", "2"):
            os.system("cls")
            break
        else:
            print(f"输入有误,[{mode}]")
    fgh = FingerprinterHack(mode)
    try:
        with open("config.ini", "r", encoding="utf-8") as f:
            configEncoding = "utf-8"
    except:
        with open("config.ini", "r", encoding="gbk") as f:
            configEncoding = "gbk"
    try:
        config = configparser.ConfigParser()
        config.read("config.ini", encoding=configEncoding)
        key_press_delay = config.getint("setting", "key_press_delay")
        key_release_delay = config.getint("setting", "key_release_delay")
        confirmationImg = config.get("setting", "confirmation_image")
        save_screenshot = config.getboolean("setting", "save_screenshot")
        fgh.key_press_delay = key_press_delay
        fgh.key_release_delay = key_release_delay
        fgh.confirmationImg = confirmationImg
        fgh.save_screenshot = save_screenshot
    except Exception as e:
        print(e)
    fgh.run()
    print(
        """需要全屏1920*1080分辨率模式\n
    \r按 F 执行扫描屏幕
    \r按 Q 暂停扫描
    """
    )
    if mode == "1":
        print("当前模式:手动触发扫描")
    else:
        print("当前模式:自动实时扫描")


if __name__ == "__main__":
    main()
