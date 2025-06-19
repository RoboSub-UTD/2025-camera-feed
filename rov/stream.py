import cv2
import numpy as np
import subprocess
import threading
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('host_ip')
args = parser.parse_args()
host_ip = args.host_ip

# Shared camera matrix and distortion
K = np.array([[522, 0.0, 320.0],
                [0.0, 522, 240.0],
                [0.0, 0.0, 1.0]], dtype=np.float32)

D = np.array([-0.2, 0.02, 0.0, 0.0], dtype=np.float32)

# GStreamer command template
def make_gst_process(w, h, port):
        return subprocess.Popen([
        "gst-launch-1.0", "fdsrc", "!",
        f"rawvideoparse", f"width={w}", f"height={h}", "format=rgb", "framerate=30/1", "!",
        "videoconvert", "!",
        "x264enc", "tune=zerolatency", "speed-preset=ultrafast", "bitrate=10000", "key-int-max=30", "intra-refresh=true", "!",
        "rtph264pay", "config-interval=1", "pt=96", "!",
        "udpsink", f"host={host_ip}", f"port={port}"
        ], stdin=subprocess.PIPE)

# Camera thread function
def stream_camera(cam_index, port, name):
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
                print(f"Camera {cam_index} failed to open.")
                return

        ret, frame = cap.read()
        if not ret:
                print(f"Camera {cam_index} failed to grab frame.")
                cap.release()
                return

        h, w = frame.shape[:2]

        # Compute remap maps
        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (w, h), np.eye(3), balance=0.05)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)

        # Start GStreamer pipeline
        proc = make_gst_process(w, h, port)

        while True:
                ret, frame = cap.read()
                if not ret:
                 break

                # Dewarp and convert to RGB
                dewarped = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
                rgb = cv2.cvtColor(dewarped, cv2.COLOR_BGR2RGB)

                try:
                        proc.stdin.write(rgb.tobytes())
                except BrokenPipeError:
                        print(f"GStreamer pipeline for camera {cam_index} closed.")
                        break


        cap.release()
        proc.stdin.close()
        proc.wait()

# Start both cameras in threads
t0 = threading.Thread(target=stream_camera, args=(0, 5000, "Camera 0"))
t1 = threading.Thread(target=stream_camera, args=(4, 5001, "Camera 4"))

t0.start()
t1.start()

t0.join()
t1.join()

