from dotenv import load_dotenv
load_dotenv(verbose=True, override=True)

import time
import argparse
from pathlib import Path
from threading import Thread
from os import environ as env

import cv2
import GPUtil
import matplotlib
import numpy as np


from utils.clock import Clock
from utils.drawer import Drawer
from utils.videoStream import VideoStream
from utils.box_choose import box_choose, choose

from det2.det2 import Det2
from deep_sort_realtime.deepsort_tracker_emb import DeepSort as Tracker

parser = argparse.ArgumentParser()
parser.add_argument("--nodisplay", action="store_true")
parser.add_argument("--time", help="flag to switch on timing", action="store_true")
args = parser.parse_args()

clock = Clock()

video_path = env.get('VIDEO_FEED',0)
video_name = env.get('VIDEO_NAME','cam')
is_webcam = bool(int(env.get('VIDEO_IS_USB_WEBCAM',1)))
if is_webcam:
    video_path = int(video_path)
flip = bool(int(env.get('VIDEO_FLIP',0)))
if flip:
    print('VIDEO WILL FLIP')
else:
    print('VIDEO WILL NOT FLIP')
video_store_raw = bool(int(env.get('VIDEO_STORE_RAW',0)))
    

stream = VideoStream(video_name, video_path, clock=clock, store_raw=video_store_raw, queueSize=5)
vid_info = stream.getInfo()
print(vid_info)

out_vid = None
write_out_vid = bool(int(env.get('WRITE_OUTPUT_VIDEO',0)))
if write_out_vid:
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    vid_out_dir = Path(env.get('WRITE_OUTPUT_VIDEO_PATH','./out/'))
    vid_out_dir.mkdir(parents=True, exist_ok=True)
    vid_out_name = env.get('WRITE_OUTPUT_VIDEO_NAME')
    if not vid_out_name:
        vid_out_name = 'out'
    out_path = vid_out_dir / f"{vid_out_name}.avi"
    out_fps = int(env.get('WRITE_OUTPUT_VIDEO_FPS',10))
    out_vid = cv2.VideoWriter(
        str(out_path),
        fourcc,
        out_fps,
        (int(vid_info["width"]), int(vid_info["height"])),
    )
    print(f'Outputting video to {out_path}')

od_thresh = float(env.get('OD_THRESH',0.4))
assert od_thresh > 0
od_weights = env.get('OD_WEIGHT_PATH')
od_config = env.get('OD_CONFIG_PATH')
od_classes = env.get('OD_CLASSES_PATH')
od_target_classes = env.get('OD_TARGET_CLASSES')
if od_target_classes:
    od_target_classes = od_target_classes.split(',')
else:
    od_target_classes = None
od = Det2(
    bgr=True,
    thresh= od_thresh,
    weights=od_weights,
    config=od_config,
    classes_path=od_classes,
    )
print("----------OD started----------")

# assuming 7fps & 70nn_budget, tracker looks into 10secs in the past.
tracker = Tracker(
    max_age=30, nn_budget=70, override_track_class=None, clock=clock
)
print("----------Tracker started----------")

GPUtil.showUtilization()
drawer = Drawer()

display = not args.nodisplay

ptz_exists = bool(int(env.get('PTZ_EXISTS',0)))
ptz = None
if ptz_exists:
    from utils.ptzer import PTZ
    from utils.ui_controller import ui_controller
    manual_override = {"p": 0, "t": 0, "z": 0, "override": False}
    if display:
        ui_thread = Thread(target=ui_controller, args=(manual_override,))
    ptz_host_url = env.get('PTZ_HOST_URL')
    assert ptz_host_url
    ptz = PTZ(ptz_host_url, flip=flip, manual_override=manual_override)

stream.start()

if display:
    show_win_name = "detracon"
    cv2.namedWindow(show_win_name, cv2.WINDOW_NORMAL)
    mouse_dict = {"click": None}
    box_choose(show_win_name, mouse_dict)
    if ptz:
        ui_thread.start()

if ptz:
    ptz.start(
        sample_period=0.01,
        pan_setpoint=0.5,
        tilt_setpoint=0.5,
        zoom_setpoint=0.8,
    )

moving_avrg_period = 0
# frame = None
chosen_track = None
while True:
    if stream.more():
        frame = stream.read(flip=flip)
        if frame is None:
            continue
        clock.register_now()

        if args.time:
            tic = time.time()
        bbs = od.detect_get_box_in(
            frame,
            box_format="ltwh",
            classes=od_target_classes,
            buffer_ratio=0.0,
        )
        if args.time:
            toc = time.time()
            print('OD infer duration: {:0.3f}'.format(toc - tic))

        # MOTracking
        tracks = tracker.update_tracks(frame, bbs)
    
        show_frame = frame.copy()
        drawer.draw_status(show_frame, status=True)
        if display and mouse_dict["click"]:
            chosen_track = choose(
                # mouse_dict["click"], det_thread_dict["tracks"]
                mouse_dict["click"], tracks
            )
            if chosen_track:
                print(f"CHOSEN TRACK {chosen_track.track_id}")
            mouse_dict["click"] = None

        if ptz and chosen_track and chosen_track.time_since_update < 2:
            l, t, w, h = chosen_track.to_tlwh()
            ptz.update_state(
                p=(l + w / 2.0) / vid_info["width"],
                t=(t + h / 2.0) / vid_info["height"],
                z=max(w / vid_info["width"], h / vid_info["height"]),
            )        
        
        if display or out_vid:
            drawer.draw_tracks(
                show_frame,
                tracks,
                chosen_track=chosen_track
            )
        if display:
            cv2.imshow(show_win_name, show_frame)
        if out_vid:
            out_vid.write(show_frame)
    # now = time.time()
    # dur = now - past
    # moving_avrg_period = ( moving_avrg_period * frame_count + dur ) / (frame_count + 1)
    # past = now
    # print('main loop period: {}'.format(dur))
    if display:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
# Closing off
if ptz_exists:
    # sends a 0,0,0 command/stop signal to PTZ to get it to reset position after awhile.
    ptz.moveit()
    # ui_thread.on_exit()

if not stream.stopped:
    stream.stop()
cv2.destroyAllWindows()
if out_vid:
    out_vid.release()
