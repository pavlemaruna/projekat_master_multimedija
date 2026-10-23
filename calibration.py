import glob
import os

import cv2
import numpy as np

rows = 9
cols = 6
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)
objectPoints = np.zeros((rows * cols, 3), np.float32)
objectPoints[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)
objectPointsArray = []
imgPointsArray = []
example = None

for path in sorted(glob.glob('calibration*.jpg')):
    img = cv2.imread(path)
    img = cv2.resize(img, (1280, 720))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (rows, cols), None)
    if ret:
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        objectPointsArray.append(objectPoints)
        imgPointsArray.append(corners)
        if example is None:
            example = img.copy()

if not objectPointsArray:
    raise RuntimeError('Nisu pronadjeni uglovi sahovske table.')

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objectPointsArray, imgPointsArray, gray.shape[::-1], None, None
)
os.makedirs('outputs/calibration', exist_ok=True)
np.savez('outputs/calibration/calib.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

error = 0
for i in range(len(objectPointsArray)):
    imgPoints, _ = cv2.projectPoints(objectPointsArray[i], rvecs[i], tvecs[i], mtx, dist)
    measured = imgPointsArray[i].reshape(-1, 2)
    projected = imgPoints.reshape(-1, 2)
    error += cv2.norm(measured, projected, cv2.NORM_L2) / len(projected)

undistortedImg = cv2.undistort(example, mtx, dist, None, mtx)
cv2.imwrite('outputs/calibration/comparison.jpg', np.hstack((example, undistortedImg)))
print('Calibration images:', len(objectPointsArray))
print('Total error:', error / len(objectPointsArray))
print('RMS:', ret)
