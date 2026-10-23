import os
import runpy
import subprocess

import cv2
import numpy as np

from lane_detection import process_frame

VIDEO = 'project_video03.mp4'
OUTPUT = 'outputs/videos/project_video03/project_video03_output.mp4'

if not os.path.exists('outputs/calibration/calib.npz'):
    runpy.run_path('calibration.py')

with np.load('outputs/calibration/calib.npz') as calibration:
    mtx, dist = calibration['mtx'], calibration['dist']

os.makedirs('outputs/images/test2', exist_ok=True)
image = cv2.imread('test2.jpg')
process_frame(image, mtx, dist, save_steps=True)

cap = cv2.VideoCapture(VIDEO)
if not cap.isOpened():
    raise RuntimeError('Video ne moze da se otvori: ' + VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
expected = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
           '-s', f'{width}x{height}', '-r', str(fps), '-i', 'pipe:0', '-i', VIDEO,
           '-map', '0:v:0', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'fast',
           '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', OUTPUT]
encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
previous = None
frames = 0
detected = 0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result, previous = process_frame(frame, mtx, dist, previous)
        detected += previous is not None
        encoder.stdin.write(result.tobytes())
        frames += 1
        if frames % 250 == 0:
            print(f'Obradjeno: {frames}/{expected}', flush=True)
finally:
    cap.release()
    encoder.stdin.close()
    code = encoder.wait()

if code != 0 or frames != expected:
    raise RuntimeError('Video nije obradjen do kraja.')
print(f'Gotovo: {frames} kadrova, traka pronadjena u {detected}.')
print(OUTPUT)
