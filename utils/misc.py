import os 

def ping(ip, count=3):
    response = os.system("ping -c {} {}".format(count, ip))
    # and then check the response...
    if response == 0:
        return True
    else:
    	return False

def crop_bb(frame, bb, buffer=0.0):
    '''
    bb in ltrb format
    '''
    l,t,r,b = bb
    w = r - l + 1
    h = b - t + 1
    buff_w = w*buffer/2.0
    buff_h = h*buffer/2.0

    ih, iw = frame.shape[:2]
    # print(ih, iw)
    crop_l = int(max(l-buff_w, 0))
    crop_r = int(min(r+buff_w, iw-1))
    crop_t = int(max(t-buff_h, 0))
    crop_b = int(min(b+buff_h, ih-1))
    crop = frame[crop_t: crop_b, crop_l:crop_r]
    # import cv2
    # cv2.imwrite('test_crop.png',crop)
    return crop