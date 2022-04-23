import cv2
import sys
import os
import numpy as np

class PosEstimation():
    
    def __init__(self, image_file_name):
        self.image_file_name = image_file_name

    def isWhite(self, y, x,r,img,crit):
        img_crop=img[x-r:x+r,y-r:y+r]
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
        #print(res)
        #cv2plt(img_crop)
        if res>crit:
            return True
        return False

    def getAllBalls(self, debug, p1, p2, white_crit):
        img = cv2.imread(self.image_file_name)
        img_draw=img.copy()
        if debug:
            print(img.shape)
            cv2plt(img)
        img = cv2.medianBlur(img, 3)
        thred = 20
        circles1 = cv2.HoughCircles(img[:, :, 1], cv2.HOUGH_GRADIENT, 1, 25, param1=p1, param2=p2, minRadius=10, maxRadius=30)
        circles0 = cv2.HoughCircles(img[:, :, 0], cv2.HOUGH_GRADIENT, 1, 25, param1=p1, param2=p2, minRadius=10, maxRadius=30)
        circles2 = cv2.HoughCircles(img[:, :, 2], cv2.HOUGH_GRADIENT, 1, 25, param1=p1, param2=p2, minRadius=10, maxRadius=30)

        circles = circles1[0, :]

        for c in circles0[0, :]:
            duplicate = False
            for cc in circles:
                pc = np.array([c[0], c[1]])
                pcc = np.array([cc[0], cc[1]])
                dis = np.linalg.norm(pc-pcc)
                if dis < thred:
                    duplicate = True
                    break
            if not duplicate:
                circles = np.append(circles, [c], axis=0)

        for c in circles2[0, :]:
            duplicate = False
            for cc in circles:
                pc = np.array([c[0], c[1]])
                pcc = np.array([cc[0], cc[1]])
                dis = np.linalg.norm(pc-pcc)
                if dis < thred:
                    duplicate = True
                    break
            if not duplicate:
                circles = np.append(circles, [c], axis=0)


        pockets = sorted(circles, key=lambda c: c[1])
        u_value = pockets[0][1]
        l_value = pockets[-1][1]
        thred_p = 20
        u_cnt = 0
        l_cnt = 0
        for u_i in pockets:
            if abs(u_i[1] - u_value) < thred_p:
                u_cnt += 1
            else:
                break
        for l_ii in range(len(pockets)-1, -1, -1):
            l_i = pockets[l_ii]
            if abs(l_i[1] - l_value) < thred_p:
                l_cnt += 1
            else:
                break
        upper = pockets[:u_cnt]
        lower = pockets[-l_cnt:]
        balls = pockets[u_cnt:-l_cnt]

        if debug:
            for i in balls:
                # draw the outer circle
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
            cv2plt(img)
            print(len(balls))

        upper = np.array(sorted(upper, key=lambda i:i[0]))
        lower = np.array(sorted(lower, key=lambda i:i[0]))

        u = sum(upper[:, 1]) / len(upper)
        l = sum(lower[:, 1]) / len(lower)
        w_in_img = l - u
        w_in_unity = 3.94
        ratio = w_in_unity / w_in_img

        # print(upper)
        # print(lower)
        center_y = (u + l) / 2
        u_x = 639.5
        for u_x_i in range(1, len(upper)):
            if upper[u_x_i][0] - upper[u_x_i-1][0] > 200:
                u_x = upper[u_x_i][0]
                break

        l_x = 639.5
        for l_x_i in range(1, len(lower)):
            if lower[l_x_i][0] - lower[l_x_i-1][0] > 200:
                l_x = lower[l_x_i][0]
                break
        center_x = (u_x + l_x) / 2

        white_ball = []
        other_ball = []
        for ball in balls:
            x = ball[0]
            y = ball[1]
            r = ball[2]
            x_in_img = y - center_y
            y_in_img = center_x - x
            x_in_unity = x_in_img * ratio
            y_in_unity = y_in_img * ratio
            if self.isWhite(int(x),int(y),int(r),img_draw,white_crit):
                white_ball.append([x_in_unity, y_in_unity])
            else:
                other_ball.append([x_in_unity, y_in_unity])
        return white_ball, other_ball