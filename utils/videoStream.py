#!/usr/bin/python3
import sys
import cv2
from pathlib import Path
import numpy as np
from queue import Queue
from threading import Thread
from collections import deque
import time

class VideoStream:
    def __init__(self, camName, vidPath, clock, queueSize=5, writeDir='./outFrames/', store_raw=False, reconnectThreshold=20, ):
        # self.stream = cv2.VideoCapture(vidPath, cv2.CAP_GSTREAMER)
        self.stream = cv2.VideoCapture(vidPath)
        self.camName = camName
        self.vidPath = vidPath
        # now, VideoStream is never stopped, just waits in a while True loop for the next ret frame.
        self.stopped = False 
        self.Q = deque(maxlen=queueSize)
        assert self.stream.isOpened(), 'error opening video file'
        print('VideoStream for {} initialised!'.format(self.camName))
        self.writeDir = Path(writeDir)
        self.writeDir.mkdir(parents=True, exist_ok=True)
        self.writeCount = 1
        self.reconnectThreshold = reconnectThreshold
        self.pauseTime = None
        assert clock is not None
        self.clock = clock
        self.today = self.clock.get_now_SGT().date()
        self.read_frame_count = 0
        self.store_raw = store_raw

    def getInfo(self):
        video_info = {}
        video_info['width'] = int(self.stream.get(3))
        video_info['height'] = int(self.stream.get(4))
        video_info['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
        # video_info['start_time'] = 0 #in secs elapsed
        # video_info['context'] = context
        # video_info['cam'] = cam
        return video_info

    def start(self):
        t = Thread(target=self._update, args=())
        t.daemon = True
        t.start()
        print('VideoStream started')
        # return self

    def reconnect_start(self):
        s = Thread(target=self.reconnect, args=())
        s.daemon = True
        s.start()

    def _update(self):
        while True:
            # if self.stopped:
                # return
            assert self.stream.isOpened(),'OHNO STREAM IS CLOSED.'
            try:
                # print(self.camName,'trying to grab')
                ret, frame = self.stream.read()
                if ret: 
                    self.Q.appendleft(frame)
                    # print('Grabbed')
            except Exception as e:
                print('stream.grab error:{}'.format(e))
                ret = False
            if not ret:
                # print(self.camName,'no Ret!')
                if self.pauseTime is None:
                    self.pauseTime = time.time()
                    self.printTime = time.time()
                    print('No frames for {}, starting {:0.1f}sec countdown to reconnect.'.\
                            format(self.camName,self.reconnectThreshold))
                time_since_pause = time.time() - self.pauseTime
                time_since_print = time.time() - self.printTime
                if time_since_print > 5: #prints only every 5 sec
                    print('No frames for {}, reconnect starting in {:0.1f}sec'.\
                            format(self.camName,self.reconnectThreshold-time_since_pause))
                    self.printTime = time.time()
                        
                if time_since_pause > self.reconnectThreshold:
                    self.reconnect_start()
                    break
                continue
                # self.stop()
                # return
            # if not self.Q.full():
            self.pauseTime = None
            # if ret:
                # ret, frame = self.stream.retrieve()
                # print(self.camName,'ret for retrieve:',ret)
                # print(frame.shape)

    def update_read_frame_count(self):
        if self.clock.get_now_SGT().date() != self.today:
            self.read_frame_count = 0
            self.today = self.clock.get_now_SGT().date()
        else:
            self.read_frame_count += 1
    import time
    def read(self, flip=False):
        if self.more():
            if flip:
                self.currentFrame = np.flip(self.Q.pop(), (0,1))
            else:
                self.currentFrame = self.Q.pop()
            if self.store_raw:
                tic = time.time()
                self.capture()
                toc = time.time()
                print(f'capture time {toc-tic}')
        self.update_read_frame_count()
        return self.currentFrame

    def more(self):
        # return self.Q.qsize() > 0
        return bool(self.Q)

    def stop(self):
        self.stopped = True
        self.stream.release()

    def capture(self):
        path = self.writeDir / f'{self.camName}_{self.today:%y%m%d}_{self.read_frame_count}.png'
        cv2.imwrite(str(path), self.currentFrame)

    def reconnect(self):
        print('Reconnecting to',self.camName)
        self.stream.release()
        self.Q.clear()
        while not self.stream.isOpened():
            self.stream = cv2.VideoCapture(self.vidPath)
        assert self.stream.isOpened(), 'error opening video file'
        print('VideoStream for {} initialised!'.format(self.vidPath))
        self.pauseTime = None
        self.start()