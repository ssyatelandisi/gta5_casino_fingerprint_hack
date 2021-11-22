import cv2

im = cv2.imread("screenshot0.png", 0)
cv2.imwrite("test.png", im[133:178, 470:558])
