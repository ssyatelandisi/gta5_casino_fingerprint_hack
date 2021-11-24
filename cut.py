"""
对screenshot截图文件识别切片保存到slices.dat
"""
import cv2
import pickle
import math

"""窗口1914*1051"""
base = (486, 288)
effect = 140
size = 119
In = 7  # 裁剪内缩
size_on = 135  # 放大后大小

"""全屏1920*1080"""
# base = (475, 271)
# effect = 144
# size = 118
# In = 8  # 裁剪内缩
# size_on = 131  # 放大后大小

files = (
    "screenshot0.png",
    "screenshot1.png",
    "screenshot2.png",
    "screenshot3.png",
)


class Data:
    def __init__(self) -> None:
        self.imgTuple = tuple()
        self.positionsRange = tuple()
        self.base = (475, 271)
        self.effect = 144
        self.size = 118
        self.region = (
            self.base[0],
            self.base[1],
            self.base[0] + self.effect + self.size,
            self.base[1] + 3 * self.effect + self.size,
        )
        self.In = 8  # 裁剪内缩
        self.size_on = 131  # 放大后大小


def cut(size_on):
    data = Data()
    with open("slices.dat", "wb") as f:
        imgArr = list()
        dist = list()  # 差异结果
        for i, file in enumerate(files):
            imgArr.append(list())
            screenshot = cv2.imread(file, 0)
            im = screenshot[140:680, 960:1330]
            save_index = 0
            positionsRange = list()
            for index in range(8):
                x = base[0] + effect * (index % 2)
                y = base[1] + effect * (index // 2)
                top = y + In
                right = x + size - In
                bottom = y + size - In
                left = x + In
                templ_src = screenshot[top:bottom, left:right]
                positionsRange.append(
                    (
                        (
                            math.ceil(left - In / 2 - base[0]),
                            math.ceil(left + In / 2 - base[0]),
                        ),
                        (
                            math.ceil(top - In / 2 - base[1]),
                            math.ceil(top + In / 2 - base[1]),
                        ),
                    )
                )
                templ = cv2.resize(templ_src, (size_on, size_on))
                res = cv2.matchTemplate(im, templ, cv2.TM_SQDIFF_NORMED)
                minV, maxV, minLoc, maxLoc = cv2.minMaxLoc(res)
                dist.append(minV)
                if minV > 0.3:
                    continue
                imgArr[i].append(templ_src)
                save_index += 1
        dist.sort()
        print(dist[:16][-1], size_on)
        data.imgTuple = tuple(imgArr)
        data.positionsRange = tuple(positionsRange)
        pickle.dump(data, f)


if __name__ == "__main__":
    cut(size_on)
    with open("slices.dat", "rb") as f:
        data = pickle.load(f)
        print(data.imgTuple)
        # cv2.imshow("test", data.imgTuple[0][0])
        # cv2.waitKey()
        # cv2.destroyAllWindows()
