import cv2
import numpy as np
import copy
# import seaborn as sns

class Drawer(object):
    def __init__(self, color = (255,255,0), font=cv2.FONT_HERSHEY_DUPLEX):
        self.color = color
        # self.color_palette = np.array(sns.color_palette("hls", 8)) * 255
        self.RED = (0,0,255)
        self.LESSRED = (0,20,100)
        self.TEAL = (148, 184, 0)
        self.font = font
        self.fontScale = 1
        self.fontThickness = 2
        self.indFontScale = self.fontScale * 2.5
        self.indFontThickness = self.fontThickness * 2
        self.indTextSize = cv2.getTextSize(text=str('1'), fontFace=self.font, fontScale=self.indFontScale, thickness=self.indFontThickness)[0]

    def _resize(self, frame):
        height, width = frame.shape[:2]
        if height != self.frameHeight:
            scale = float(height) / self.frameHeight
            frame = cv2.resize(frame, (int(width / scale), int(self.frameHeight) ) )
        return frame

    def _put_label(self, frame, label):
        border=3
        cv2.putText(frame, label, (border,20+border),
                    self.font, self.fontScale, 
                    self.color, self.fontThickness)

    def draw_chosen(self, frameDC, track):
        # for pluggy don't draw!
        return 
        if track:
            msg = 'FOLLOWING: {}'.format(track.track_id)
            color = (0,255,0)
        else:
            msg = 'FOLLOWING: NIL'
            color = self.color
        fontScale = 1.2
        fontThickness = 3
        # print(frameDC.shape)
        cv2.putText(frameDC, msg, (frameDC.shape[1]-310,10+24), self.font, fontScale, color, fontThickness)
        # cv2.putText(frameDC, msg, (frameDC.shape[1]-20,10+24), self.font, fontScale, self.color, fontThickness)

    def draw_status(self, frameDC, status):
        if status:
            status_msg = 'DET: ON'
        else:
            status_msg = 'DET: OFF'
        fontScale = 0.75
        fontThickness = 2
        cv2.putText(frameDC, status_msg, (10,10+24), self.font, fontScale, self.color, fontThickness)

    def draw_track(self, frameDC, track, chosen_track=None, tuning=False):
        if chosen_track and chosen_track.track_id == track.track_id:
            color = (255,255,255) # WHITE
        else:
            color = self.color
        
        buffer = 3
        nextline=25
        fontScale = 1 * 0.7
        fontThickness = 1
        smallFontScale = fontScale * 0.5

        l,t,r,b = [int(x) for x in track.to_tlbr()]
        
        text = 'Trk {}, Class {}'.format(track.track_id.split('_')[1], track.det_class)

        main_text_size, text_baseline = cv2.getTextSize(text, self.font, fontScale, fontThickness)
        main_text_w, main_text_h = main_text_size
        # print('MAIN TEXT W: {} H: {} BL: {}'.format(text_w, text_h, text_baseline))
        cv2.putText(frameDC, 
                    text, 
                    # (l+5, b-10),
                    (l+5, b - buffer),
                    self.font, fontScale, color, fontThickness)

        cv2.rectangle(frameDC, (l, t), (r, b), color, fontThickness)


        # Det confidence
        if track.det_conf:
            det_text = 'Det @ {:.0f}%'.format(track.det_conf * 100)
        else:
            det_text = 'Det @ None'

        small_text_size, small_text_baseline = cv2.getTextSize(det_text, self.font, smallFontScale, fontThickness)
        small_text_w, small_text_h = small_text_size
        cv2.putText(frameDC, 
                    det_text, 
                    # (l+5, b-10-nextline),
                    (l+5, b - buffer - main_text_h - (buffer)*1), 
                    self.font, smallFontScale, color, fontThickness)

    def draw_tracks(self, frameDC, tracks, chosen_track=None, bigSmall=False, tuning=False):
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            self.draw_track(frameDC, track, chosen_track, tuning=tuning)

    def draw_bbs(self, frameDC, bbs, label=''):
        if bbs is None or len(bbs) == 0:
            return
        # frameDC = copy.deepcopy(frame)
        frame_h, frame_w = frameDC.shape[:2]
        for i, bb in enumerate(bbs):
            if bb is None:
                continue
            l,t,w,h = [ int(x) for x in bb[0]]
            r = l + w - 1
            b = t + h - 1
            text = bb[2]
            cv2.rectangle(frameDC, (l,t), (r,b), self.color, 2)
            cv2.putText(frameDC, 
                        text, 
                        (l+5, b-10),
                        self.font, self.fontScale, self.color, self.fontThickness)

            if t - 10 - self.indTextSize[1] >= 0: 
                text_y = int(t - 10)
            elif b + 10 + self.indTextSize[1] <= frame_h - 1:
                text_y = int(b + 10 + self.indTextSize[1])
            else:
                text_y = int(t + (b-t)/2 + self.indTextSize[1]/2)

            cv2.putText(frameDC, 
                        str(i), 
                        (l+5, text_y),
                        self.font, self.fontScale*2.5, self.color, self.fontThickness*2)
        self._put_label(frameDC, label)
        # return frameDC

    def draw_label(self, frame, label=''):
        frameDC = copy.deepcopy(frame)
        self._put_label(frameDC, label)
        return frameDC

    def draw_dets(self, frame, dets, color=None, label=''):
        if dets is None or len(dets) == 0:
            return frame
        if color is None:
            color = self.color
        frameDC = copy.deepcopy(frame)
        self._put_label(frameDC, label)
        for det in dets:
            # det = ( class, confidence , (x, y, w, h) )
            l = int(det[2][0] - det[2][2]/2)
            t = int(det[2][1] - det[2][3]/2)
            r = int(det[2][0] + det[2][2]/2)
            b = int(det[2][1] + det[2][3]/2)
            text = '{}: {:0.2f}%'.format(det[0].decode("utf-8"), det[1]*100)
            cv2.rectangle(frameDC, (l,t), (r,b), color, 2)
            cv2.putText(frameDC, 
                        text, 
                        (l+5, b-10),
                        self.font, self.fontScale, color, self.fontThickness)
        return frameDC

    def draw_bb_tracking(self, frame, bb, name, generated=False, last_tracked=False, det_asst=True, took_det=(None, None), label=''):
        if generated:
            color = self.RED # red
            label = 'TRACK{}'.format('+DETECT' if det_asst else '-NODETECT')
            if took_det[0] is not None:
                label += ': {} '.format('det' if took_det[0] else 'trk') 
                label += '{:0.1f}'.format(took_det[1]) if took_det[0] else ''
        elif last_tracked:
            color = self.LESSRED # reddish brown
            label = 'TRACK{}'.format('+DETECT' if det_asst else '-NODETECT')
        else:
            color = self.TEAL
            label = 'NO-TRACK'
        return self.draw_bb_name(frame, bb, name, color=color, label=label)
