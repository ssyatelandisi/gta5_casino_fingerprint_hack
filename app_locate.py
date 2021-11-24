"""
通过本地已保存好的指纹切片对比方法
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
import pickle


class Data:
    def __init__(self) -> None:
        self.imgTuple = tuple()
        self.positionsRange = tuple()
        self.base = (486, 288)
        self.effect = 140
        self.size = 119
        self.In = 7  # 裁剪内缩
        self.size_on = 135  # 放大后大小


class FingerprinterHack:
    def __init__(self, mode="1"):
        self.__mode = mode
        self.__onoff = False
        self.__key_press_delay = 0.05
        self.__key_release_delay = 0.05
        self.__save_screenshot = False
        self.__positionsRange = (
            ((0, 0), (59, 59)),
            ((144, 0), (203, 59)),
            ((0, 144), (59, 203)),
            ((144, 144), (203, 203)),
            ((0, 288), (59, 347)),
            ((144, 288), (203, 347)),
            ((0, 432), (59, 491)),
            ((144, 432), (203, 491)),
        )
        self.__currentGroupIndex = 99
        self.__pos = []
        self.__threadPool = []
        self.__pics = ()
        self.__region = ()

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
    def save_screenshot(self):
        return self.__save_screenshot

    @save_screenshot.setter
    def save_screenshot(self, status: bool):
        self.__save_screenshot = status

    @property
    def pics(self):
        return self.__pics

    @pics.setter
    def pics(self, value: tuple):
        self.__pics = value

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, value: tuple):
        self.__region = value

    @property
    def positionsRange(self):
        return self.__positionsRange

    @positionsRange.setter
    def positionsRange(self, value: tuple):
        self.__positionsRange = value

    def onoff(self, status: bool):
        """设置开关状态\n
        status bool: True开启|False关闭\n
        """
        self.__onoff = status
        if status is True:
            Beep(1600, 600)
        else:
            Beep(600, 600)

    def main_thread(self):
        """主线程"""
        while True:
            if self.__onoff is False:
                time.sleep(0.1)
                continue
            else:
                self.__pos.clear()
                self.__threadPool.clear()
                img = cv2.cvtColor(
                    np.asanyarray(ImageGrab.grab(bbox=self.__region)),
                    cv2.COLOR_RGB2GRAY,
                )
                for groupIndex in range(4):
                    th = threading.Thread(
                        target=self.compare_group,
                        args=(img, groupIndex),
                    )
                    self.__threadPool.append(th)
                    th.start()
                for th in self.__threadPool:
                    th.join()
                self.__threadPool.clear()
                if self.__currentGroupIndex >= 4:
                    time.sleep(0.025)  # 游戏帧数的倒数，作为每一次扫描的间隔
                    continue
                if self.__save_screenshot is True:
                    ImageGrab.grab().save(f"screenshot{self.__currentGroupIndex}.png")
                for pic in self.__pics[self.__currentGroupIndex][1:4]:  # 当前组剩余3长匹配
                    th = threading.Thread(
                        target=self.compare_rest,
                        args=(
                            img,
                            pic,
                        ),
                    )
                    self.__threadPool.append(th)
                    th.start()
                for th in self.__threadPool:
                    th.join()
                self.__pos.sort()
                currentPos = 0
                for pos in self.__pos:
                    dis = pos - currentPos
                    self.send_key("s", dis // 2)
                    self.send_key("d", dis % 2)
                    self.send_key("enter", 1)
                    self.send_key("tab", 1)
                    currentPos = pos
                self.__currentGroupIndex = 99
                if self.__mode == "1":
                    self.onoff(False)
                else:
                    time.sleep(4.15)

    def compare_group(self, img, groupIndex: int):
        """对比查出符合哪一组\n
        img: 匹配目标\n
        groupIndex int: 0-7\n
        """
        with threading.Lock():
            templ = self.__pics[groupIndex][0]
            minV, maxV, minLoc, maxLoc = self.matchTemplate(img, templ, cv2.TM_SQDIFF_NORMED)
            if minV < 0.1:
                self.__currentGroupIndex = groupIndex
                self.__pos.append(self.get_position(minLoc))

    def compare_rest(self, img, templ):
        """对比查出格子位置索引\n
        img: 匹配目标\n
        templ: 匹配模板\n
        """
        with threading.Lock():
            minV, maxV, minLoc, maxLoc = self.matchTemplate(img, templ, cv2.TM_SQDIFF_NORMED)
            if minV < 0.1:
                self.__pos.append(self.get_position(minLoc))

    def matchTemplate(self, image, templ, method):
        """模板匹配分装\n
        image: 匹配对象\n
        templ: 模板对象\n
        method: 匹配算法\n
        return cv2.minMaxLoc\n
        """
        return cv2.minMaxLoc(cv2.matchTemplate(image, templ, method))

    def get_position(self, loc: "tuple[float, float]"):
        """获取0-8个格子位置索引\n
        loc tuple[x: float, y: float]: 坐标位置\n
        return int: 格子位置索引\n
        """
        for i in range(8):
            if (
                self.__positionsRange[i][0][0] <= loc[0] < self.__positionsRange[i][0][1]
                and self.__positionsRange[i][1][0] <= loc[1] < self.__positionsRange[i][1][1]
            ):
                return i
            else:
                continue

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

    def status_thread(self):
        """开关控制线程"""
        keyboard.add_hotkey("f", self.onoff, args=(True,))  # 开启
        keyboard.add_hotkey("q", self.onoff, args=(False,))  # 关闭

    def run(self):
        threading.Thread(target=self.status_thread).start()
        threading.Thread(target=self.main_thread).start()


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
        save_screenshot = config.getboolean("setting", "save_screenshot")
        config_data = config.get("setting", "data")
        fgh.key_press_delay = key_press_delay
        fgh.key_release_delay = key_release_delay
        fgh.save_screenshot = save_screenshot
        with open(config_data, "rb") as f:
            data = pickle.load(f)
        fgh.pics = data.imgTuple
        fgh.positionsRange = data.positionsRange
        fgh.region = data.region
        fgh.run()
    except Exception as e:
        print(e)
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
