from pprint import pprint
from threading import Thread
import time
from hikvisionapi import Client
from simple_pid import PID
import numpy as np

def package_xml( pan=0, tilt=0, zoom=0 ):
    return '<PTZData><pan>{}</pan><tilt>{}</tilt><zoom>{}</zoom></PTZData>'.format( pan, tilt, zoom )

class PTZ:
    def __init__(self, host_url, user='admin', pwd='password123', flip=False, manual_override=None):
        self.api = Client(host_url, user, pwd)
        self.flip = flip
        self.manual_override = manual_override
    #     if init_ptz:
    #         self.init_ptz()

    # def init_ptz(self):
    #     print('Initialising ptz postition..')
    #     self.moveit(p=75)
    #     time.sleep(15)
    #     print('Inited ptz postition..')


    # takes speed values for each p,t,z
    # for pan, positive is left, negative is right
    # for tilt, positive is up, negative is down
    def moveit(self, p=0, t=0, z=0):
        p = int(p if self.flip else -p)
        t = int(-t)
        z = int(z)
        # print('Sending PTZ speeds: p(left) {}, t(up) {}, z {}'.format(p,t,z))
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(pan=p, tilt=t, zoom=z) )
        except Exception as e:
            print('moveit error: {}'.format(e))

    def _update(self):
        self.past = time.time()
        print('STARTING PTZ MOVEMENT')
        while True:
            now = time.time()
            if (now - self.past) < self.sample_period:
                continue 
            self.past = now
            if self.manual_override['override']:
                # print('[PTZ MOVEMENT] Manual Override', self.manual_override)
                self.moveit(p=self.manual_override['p'], t=self.manual_override['t'], z=self.manual_override['z'] )
            else:
                # print('[PTZ MOVEMENT] PID control')
                # if abs(self.ptz_values['p']) > abs(self.ptz_values['t']):
                #     self.moveit(p=self.ptz_values['p'], t=0, z=0)
                # else:
                #     self.moveit(p=0, t=self.ptz_values['t'], z=0)
                self.moveit(p=self.ptz_values['p'], t=self.ptz_values['t'], z=self.ptz_values['z'])

    # sample period in secs
    def start(self, sample_period=0.01, pan_setpoint=0.5, tilt_setpoint=0.5, zoom_setpoint=0.8):
        '''
        `setpoint` is the value that the PID is trying to achieve. 
        - for pan and tilt setpoints, normalised against the frame width and height. 0.5 means we want to keep the target bounding box in the middle.
        - for zoom_setpoint, normalised against frame size also, want to strive for the bounding box to be 0.8 of the frame size (only for the larger side of the box)   
        '''

        print('PTZ starting with Sample Period: {}'.format(sample_period))
        self.sample_period = sample_period
        self.pan_setpoint = pan_setpoint
        self.tilt_setpoint = tilt_setpoint
        self.zoom_setpoint = zoom_setpoint
        print('PTZ pan setpoint: {}'.format(self.pan_setpoint))
        print('PTZ tilt setpoint: {}'.format(self.tilt_setpoint))

        # self.pan_warm_zone = pan_warm_zone
        # self.tilt_warm_zone = tilt_warm_zone
        # self.zoom_warm_zone = zoom_warm_zone
        # self.pan_warm_amp = pan_warm_amp
        # self.tilt_warm_amp = tilt_warm_amp
        # self.zoom_warm_amp = zoom_warm_amp

        # self.pan_pid = PID(240, 1, 50000, setpoint = self.pan_setpoint)
        self.pan_pid = PID(200, 0, 0, setpoint = self.pan_setpoint)
        # self.pan_pid = PID(150, 0, 0, setpoint = self.pan_setpoint)
        # self.pan_pid = PID(200, 100, 100, setpoint = self.pan_setpoint)
        # self.pan_pid = PID(0, 0, 0, setpoint = self.pan_setpoint)
        # self.tilt_pid = PID(240, 1, 10000, setpoint = self.tilt_setpoint)
        # self.tilt_pid = PID(220, 1, 10000, setpoint = self.tilt_setpoint)
        self.tilt_pid = PID(200, 0, 0, setpoint = self.tilt_setpoint)
        # self.tilt_pid = PID(0, 0, 0, setpoint = self.tilt_setpoint)
        # self.zoom_pid = PID(15, 0, 0, setpoint = self.zoom_setpoint)
        self.zoom_pid = PID(10, 0, 0, setpoint = self.zoom_setpoint)
        # self.zoom_pid = PID(0, 0, 0, setpoint = self.zoom_setpoint)
        # self.zoom_pid = PID(25, 0, 0, setpoint = self.zoom_setpoint)

        self.ptz_values = {'p':0., 't':0., 'z':0.}
        self.ptz_thread = Thread(target=self._update, args=())
        self.ptz_thread.daemon = True
        self.ptz_thread.start()
        print('PTZ thread started')

    # in pixels, p=bb.centre_x, t = bb.centre_y
    # def update_state(self, p=0, t=0, z=0):
    # def update_state(self, p=self.pan_setpoint, t=self.tilt_setpoint, z=0):
    def update_state(self, p=None, t=None, z=None):
        if p is None:
            p = self.pan_setpoint
        if t is None:
            t = self.tilt_setpoint
        if z is None:
            z = self.zoom_setpoint
        # print('Current state, p:{}, t:{}'.format(p, t))
        # print('PTZ pan setpoint: {}'.format(self.pan_setpoint))
        # print('PTZ tilt setpoint: {}'.format(self.tilt_setpoint))

        self.ptz_values['p'] = self.pan_pid(p)
        self.ptz_values['t'] = self.tilt_pid(t)
        self.ptz_values['z'] = self.zoom_pid(z)

    # def scan(self,):
        # self.moveit(p=,t=,z=)    

    def pan_left(self, speed=60, dur_sec=1.):
        print('Pan Left')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(pan=-speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )
        except Exception as e:
            print(e)
            
    def pan_right(self, speed=60, dur_sec=1.):
        print('Pan Right')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(pan=speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )    
        except Exception as e:
            print(e)

    def tilt_up(api, speed=60, dur_sec=1.):
        print('Tilt Up')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(tilt=speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )     
        except Exception as e:
            print(e)
       

    def tilt_down(api, speed=60, dur_sec=1.):
        print('Tilt Down')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(tilt=-speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )
        except Exception as e:
            print(e)

    def zoom_in(api, speed=60, dur_sec=1.):
        print('Zoom In')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(zoom=speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )
        except Exception as e:
            print(e)

    def zoom_out(api, speed=60, dur_sec=1.):
        print('Zoom Out')
        try:
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml(zoom=-speed) )
            time.sleep( dur_sec )
            self.api.PTZCtrl.channels[1].continuous(method='put', data=package_xml() )        
        except Exception as e:
            print(e)


if __name__ == '__main__':
    host = '192.168.0.4'
    host_url = 'http://{}'.format(host)
    ptz = PTZ(host_url, init_ptz=False)
    # ptz.moveit(p=75)
    # ptz.moveit(p=-75)
    # ptz.moveit(t=25)
    # ptz.moveit(t=-25)
    ptz.moveit()
    # ptz = PTZ(host_url, init_ptz=True)
