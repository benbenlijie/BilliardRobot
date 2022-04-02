import cv2
import sys
import os
import numpy as np

class PosEstimation():
    
    def __init__(self, image_file_name):
        self.image_file_name = image_file_name
    
    def isWhite(self, y, x, r):
        #define img here
        img = cv2.imread(self.image_file_name)
        x = int(x)
        y = int(y)
        r = int(r)
        img_crop=(img[x-r:x+r,y-r:y+r])
        hsv_img = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)
        COLOR_MIN = np.array([0, 0, 200],np.uint8)      
        COLOR_MAX = np.array([179, 60, 255],np.uint8) 
        frame_threshed = cv2.inRange(hsv_img, COLOR_MIN, COLOR_MAX)
        cnt=0
        for i in range(frame_threshed.shape[0]):
            for j in range(frame_threshed.shape[1]):
                if frame_threshed[i][j]==255:
                    cnt+=1
        res=cnt/(r*r)
        if res>2:
            return True
        return False

    def getAllBalls(self, debug):
        img = cv2.imread(self.image_file_name)
        if debug:
            print(img.shape)
        circles = cv2.HoughCircles(img[:, :, 1], cv2.HOUGH_GRADIENT, 1, 20,
                              param1=200, param2=20, minRadius=5, maxRadius=30)
        # circles = np.uint16(np.around(circles))
        if debug:
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                # sli=img2[i[1]-i[2]:i[1]+i[2],i[0]-i[2]:i[0]+i[2]]
                # cv2plt(sli)
                # draw the center of the circle
                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
            cv2plt(img)

        pockets = sorted(circles[0,:], key=lambda c: c[1])
        upper = pockets[:3]
        lower = pockets[-3:]
        balls = pockets[3:-3]
        upper = np.array(sorted(upper, key=lambda i:i[0]))
        lower = np.array(sorted(lower, key=lambda i:i[0]))

        u = sum(upper[:, 1]) / 3
        l = sum(lower[:, 1]) / 3
        w_in_img = l - u
        w_in_unity = 3.94
        ratio = w_in_unity / w_in_img
        center_y = (u + l) / 2
        center_x = (upper[1,0] + lower[1,0]) / 2

        white_ball = []
        other_ball = []
        for ball in balls:
            x = ball[0]
            y = ball[1]
            x_in_img = y - center_y
            y_in_img = center_x - x
            x_in_unity = x_in_img * ratio
            y_in_unity = y_in_img * ratio

            if self.isWhite(ball[0], ball[1], ball[2]):
                white_ball.append([x_in_unity, y_in_unity])
            else:
                other_ball.append([x_in_unity, y_in_unity])
        
        return white_ball, other_ball