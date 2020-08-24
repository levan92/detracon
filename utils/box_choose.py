import cv2
import copy 

mouse_pt = None

def choose(clickpt, tracks):
    if clickpt:
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            l,t,r,b = track.to_tlbr()
            if l <= clickpt[0] <= r and t <= clickpt[1] <= b:
                return track
                # return track.track_id
    return None

def mouse_move(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        move_pt = (x,y)
    if event == cv2.EVENT_LBUTTONDOWN:
        click_pt = (x,y)
        param['click'] = click_pt

def box_choose(show_win_name, mouse_dict):
    param = mouse_dict
    cv2.setMouseCallback(show_win_name, mouse_move, param)


if __name__ == '__main__':
    img_path =  '/home/dh/Workspace/tracknotation/cache/vid_cache/mexico_airport_drone_short_frames/3.jpg'
    frame = cv2.imread(img_path)
    show_win_name = 'show frame'
    cv2.namedWindow(show_win_name, cv2.WINDOW_NORMAL)
    mouse_dict = {'click': None}

    box_choose(show_win_name, mouse_dict)

    cv2.imshow(show_win_name,frame)
    cv2.waitKey(0)

    print(mouse_dict)

# def click_and_crop(event, x, y, flags, param):
#     # grab references to the global variables
#     global refPt, sel_rect_endpoint, cropping
 
#     # if the left mouse button was clicked, record the starting
#     # (x, y) coordinates and indicate that cropping is being
#     # performed
#     if event == cv2.EVENT_LBUTTONDOWN:
#         refPt = [(x, y)]
#         sel_rect_endpoint = refPt
#         cropping = True
#     # check to see if the left mouse button was released
#     elif event == cv2.EVENT_LBUTTONUP:
#         # record the ending (x, y) coordinates and indicate that
#         # the cropping operation is finished
#         refPt.append((x, y))
#         cropping = False
 
#         # draw a rectangle around the region of interest
#         cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
#         cv2.imshow("image", image)
#     elif event == cv2.EVENT_MOUSEMOVE and cropping:
#         sel_rect_endpoint = [(x, y)]


# if __name__ == '__main__':
#     # load the image, clone it, and setup the mouse callback function
#     image = cv2.imread('/home/dh/Pictures/lol.png')
#     clone = image.copy()
#     cv2.namedWindow("image")
#     cv2.setMouseCallback("image", click_and_crop)
#     refPt = []
#     cropping = False

#     # keep looping until the 'q' key is pressed
#     while True:
#         # display the image and wait for a keypress
#         if not cropping:
#             cv2.imshow('image', image)
#         elif cropping and sel_rect_endpoint:
#             rect_cpy = image.copy()
#             cv2.rectangle(rect_cpy, refPt[0], sel_rect_endpoint[0], (0, 255, 0), 1)
#             cv2.imshow('image', rect_cpy)
#         key = cv2.waitKey(1) & 0xFF
     
#         # if the 'r' key is pressed, reset the cropping region
#         if key == ord("r"):
#             image = clone.copy()
     
#         # if the 'c' key is pressed, break from the loop
#         elif key == ord("c"):
#             break
     
#     # if there are two reference points, then crop the region of interest
#     # from teh image and display it
#     if len(refPt) == 2:
#         roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
#         cv2.imshow("ROI", roi)
#         cv2.waitKey(0)
     
#     # close all open windows
#     cv2.destroyAllWindows()
