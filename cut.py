import cv2
import pickle

size = 129
effest = 3
xOy = (
    (481 + effest, 277 + effest, 587 - effest, 383 - effest),
    (625 + effest, 277 + effest, 731 - effest, 383 - effest),
    (481 + effest, 421 + effest, 587 - effest, 527 - effest),
    (625 + effest, 421 + effest, 731 - effest, 527 - effest),
    (481 + effest, 565 + effest, 587 - effest, 671 - effest),
    (625 + effest, 565 + effest, 731 - effest, 671 - effest),
    (481 + effest, 709 + effest, 587 - effest, 815 - effest),
    (625 + effest, 709 + effest, 731 - effest, 815 - effest),
)
files = (
    "screenshot0.png",
    "screenshot1.png",
    "screenshot2.png",
    "screenshot3.png",
)


with open("slices.dat", "wb") as f:
    cut = [[], [], [], []]
    for i, file in enumerate(files):
        screenshot = cv2.imread(file, 0)
        im = screenshot[140:680, 960:1330]
        save_index = 0
        for index in range(8):
            templ_src = screenshot[
                xOy[index][1] : xOy[index][3], xOy[index][0] : xOy[index][2]
            ]
            templ = cv2.resize(templ_src, (size, size))
            res = cv2.matchTemplate(im, templ, cv2.TM_SQDIFF_NORMED)
            minV, maxV, minLoc, maxLoc = cv2.minMaxLoc(res)
            if minV > 0.3:
                continue
            # cv2.imwrite(
            #     f"{i}_{save_index}.png",
            #     templ_src,
            #     [int(cv2.IMWRITE_PNG_COMPRESSION), 9],
            # )
            cut[i].append(templ_src)
            save_index += 1
    pickle.dump(cut, f)
with open("slices.dat", "rb") as f:
    cut = pickle.load(f)
    cv2.imshow("test",cut[0][0])
    cv2.waitKey()
    cv2.destroyAllWindows()
