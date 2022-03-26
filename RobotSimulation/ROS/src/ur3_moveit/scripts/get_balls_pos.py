import cv2
import sys
import os
import numpy as np


class PosEstimation():

    def __init__(self, image_file_name):
        self.image_file_name = image_file_name

    def getCueBallPosition(self, w, h, debug):
        # can remove
        if debug:
            origin = cv2.imread(self.image_file_name)
        img = cv2.imread(self.image_file_name)
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
        # perform thredsholding, green channel
        # plt.hist(img[:, :, 1].ravel(), 256, [0, 255], facecolor='black')
        # plt.show()
        (_, thrd) = cv2.threshold(
            img[:, :, 1], 254, 255, cv2.THRESH_BINARY_INV)
        if debug:
            cv2plt(thrd)
        src = cv2.medianBlur(thrd, 15)
        if debug:
            cv2plt(src)
        edge = cv2.Canny(src, 200, 250, 5)
        # cv2plt(edge)
        ctrs = cv2.findContours(edge, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        ctrs = ctrs[0]
        # pick the largest one
        ctrs = sorted(ctrs, key=cv2.contourArea, reverse=True)[:1]
        if debug:
            cv2.drawContours(origin, ctrs, -1, (255, 0, 225), 5)
            cv2plt(origin)
        center, radius = cv2.minEnclosingCircle(ctrs[0])
        if debug:
            print(radius)
            print(center)
        return center

    def equal(self, a, b):
        if abs(a-b) <= 6:
            return True
        else:
            return False

    def getBallsPosition(self, w, h, debug, cue_x=0, cue_y=0):
        if debug:
            origin = cv2.imread(self.image_file_name)
        img = cv2.imread(self.image_file_name)
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = cv2.inRange(img[:, :, 1], 75, 150)
        if debug:
            cv2plt(mask)
        bulk = cv2.dilate(mask, None, iterations=2)
        bulk = cv2.erode(bulk, None, iterations=6)
        if debug:
            cv2plt(bulk)
        edge = cv2.Canny(bulk, 200, 250, 5)
        if debug:
            cv2plt(edge)
        ctrs = cv2.findContours(edge, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        ctrs = ctrs[0]
        if debug:
            # contour is red
            cv2.drawContours(origin, ctrs, -1, (0, 0, 225), 2)

        min_r = 15
        max_r = 25
        min_center_x = 360
        max_center_x = 930
        min_center_y = 45
        max_center_y = 485

        res = []
        # min_dis = sys.maxsize
        for i, c in enumerate(ctrs):
            center, radius = cv2.minEnclosingCircle(c)
            x = int(center[0])
            y = int(center[1])
            # circle is green
            if debug:
                cv2.circle(origin, (x, y), int(radius), (0, 255, 0), 2)
            if min_r <= radius <= max_r and min_center_x <= x <= max_center_x and min_center_y <= y <= max_center_y:
                if self.equal(x, cue_x) and self.equal(y, cue_y):
                    continue
                # final pick is blue
                if debug:
                    cv2.circle(origin, (x, y), int(radius), (255, 0, 0), 5)
                res.append([x, y])
        if debug:
            cv2plt(origin)
        return res
        # center, radius = cv2.minEnclosingCircle(ctrs[0])
