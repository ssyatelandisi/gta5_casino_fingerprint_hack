from winsound import Beep
import keyboard
import threading
import time
import pyautogui
import os


class FingerprinterHack:
    def __init__(self, mode="1"):
        self.__mode = mode
        self.__onoff = False if mode == "1" else True
        self.__keydelay = 0.05
        self.__pics = (
            (
                "0_0.png",
                "0_1.png",
                "0_2.png",
                "0_3.png",
            ),
            (
                "1_0.png",
                "1_1.png",
                "1_2.png",
                "1_3.png",
            ),
            (
                "2_0.png",
                "2_1.png",
                "2_2.png",
                "2_3.png",
            ),
            (
                "3_0.png",
                "3_1.png",
                "3_2.png",
                "3_3.png",
            ),
        )
        self.__positionsRange = (
            (163, 177),
            (250, 265),
            (302, 315),
            (357, 372),
            (445, 457),
            (484, 498),
            (588, 600),
            (618, 632),
        )
        self.__currentGroupIndex = 99
        self.__pos = []
        self.__threadPool = []

    @property
    def keydelay(self):
        return self.__keydelay

    @keydelay.setter
    def keydelay(self, value: float):
        self.__keydelay = value / 1000

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
                for groupIndex in range(4):
                    th = threading.Thread(target=self.compare_group, args=(groupIndex,))
                    self.__threadPool.append(th)
                    th.start()
                for th in self.__threadPool:
                    th.join()
                self.__threadPool.clear()
                if self.__currentGroupIndex >= 4:
                    time.sleep(0.025)  # 游戏帧数的倒数，作为每一次扫描的间隔
                    continue

                for pic in self.__pics[self.__currentGroupIndex][1:4]:  # 当前组剩余3长匹配
                    th = threading.Thread(target=self.compare_rest, args=(pic,))
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

    def compare_group(self, groupIndex: int):
        """对比查出符合哪一组\n
        groupIndex int: 0-7\n
        """
        with threading.Lock():
            r = pyautogui.locateCenterOnScreen(
                f"./cut/{self.__pics[groupIndex][0]}",
                grayscale=True,
                region=(475, 271, 737, 821),
                confidence=0.9,
            )
            if r is not None:
                self.__currentGroupIndex = groupIndex
                self.__pos.append(self.get_position(self.get_distance(r)))

    def compare_rest(self, pic: str):
        """对比查出格子位置索引\n
        pic str: 图片名\n
        """
        with threading.Lock():
            r = pyautogui.locateCenterOnScreen(
                f"./cut/{pic}",
                grayscale=True,
                region=(475, 271, 737, 821),
                confidence=0.9,
            )
            if r is not None:
                self.__pos.append(self.get_position(self.get_distance(r)))

    def get_distance(self, xOy: "tuple[float, float]") -> float:
        """计算坐标点到基点的距离\n
        xOy tuple[float, float]: (x, y)\n
        return float: 距离\n
        """
        return ((xOy[0] - 475) ** 2 + (xOy[1] - 171) ** 2) ** 0.5

    def get_position(self, distance: float):
        """获取0-8个格子位置索引\n
        distance float: 距离\n
        return int: 格子位置索引\n
        """
        for i in range(8):
            if self.__positionsRange[i][0] <= distance <= self.__positionsRange[i][1]:
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
            time.sleep(self.__keydelay)
            keyboard.release(key)
            # time.sleep(self.__keydelay)

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
    fgh.keydelay = 30
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
