# -*- coding: utf-8 -*-

import cv2
import math
import glob
from mysql import mysql
import os

def matchCurrentFrameCarsToExisting(x, y, w, h, cx, cy, indexOfCurrentFrame):
    indexOfLeastDistance = -1
    leastDistance = 100000.0

    for car in blobs:
        car['newOrMatch'] = False

    if (indexOfCurrentFrame > 0):
        for index, car in enumerate(blobs):
            curDistance = distanceBetweenPoints(car['cx'], car['cy'], cx, cy)
            if curDistance < leastDistance:
                leastDistance = curDistance
                indexOfLeastDistance = index

    if leastDistance < 60 and blobs[indexOfLeastDistance]['beingTracked'] == True:
        addToExistingCarsArray(x, y, w, h, cx, cy, indexOfCurrentFrame, indexOfLeastDistance)
    else:
        if leastDistance > 5:
            addToCarsArray(x, y, w, h, cx, cy, indexOfCurrentFrame)

    for car in blobs:
        if car['newOrMatch'] == False:
            car['framesWithoutMatch'] += 1

        if car['framesWithoutMatch'] > 500:
            car['beingTracked'] == False
            car['cx'] = 1000
            car['cy'] = 1000
            car['x'] = 1000
            car['y'] = 1000
            car['newOrMatch'] = False


def distanceBetweenPoints(x1, y1, x2, y2):
    intX = abs(x1 - x2)
    intY = abs(y1 - y2)
    return math.sqrt(math.pow(intX, 2) + math.pow(intY, 2))


def addToCarsArray(x, y, w, h, cx, cy, curFrameIndex):
    blobs.append({'x': x, 'y': y, 'w': w, 'h': h, 'cx': cx, 'cy': cy, 'beingTracked': True, 'newOrMatch': True, 'framesWithoutMatch': 0, 'prevCenterX': 0, 'prevCenterY': 0, 'hasCrossed': False})


def addToExistingCarsArray(x, y, w, h, cx, cy, curFrameIndex, vehicleIndex):
    prevCenterX = blobs[vehicleIndex]['cx']
    prevCenterY = blobs[vehicleIndex]['cy']
    prevW = blobs[vehicleIndex]['w']
    prevH = blobs[vehicleIndex]['h']
    hasCrossed = blobs[vehicleIndex]['hasCrossed']
    blobs[vehicleIndex] = {'x': x, 'y': y, 'w': prevW, 'h': prevH, 'cx': cx, 'cy': cy, 'beingTracked': True, 'newOrMatch': True, 'framesWithoutMatch': 0, 'prevCenterX': prevCenterX, 'prevCenterY': prevCenterY, 'hasCrossed': hasCrossed}


def showCars(currentFrameIndex):
    for index, cars in enumerate(blobs):
        # print index
        if cars['beingTracked'] == True:

            cars['newOrMatch'] += 1
            if cars['newOrMatch'] > 30:
                cars['beingTracked'] = False

        cv2.rectangle(crop_img, (cars['x'], cars['y']), (cars['x']+cars['w'], cars['y'] + cars['h'] ), (0, 255, 255), 2)
        cv2.putText(crop_img, str(index), (cars['x'], cars['y']), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

def ifCarsCrossedLineLeft():
    rightCrossed = 0
    leftCrossed  = 0
    for index, cars in enumerate(blobs):
        if cars['beingTracked'] == True and cars['hasCrossed'] == False:
            print str(index) + ': c ' + str(cars['cx']) + ' p ' + str(cars['prevCenterX'])
            if cars['prevCenterX'] != 0 and abs(cars['cx'] != cars['prevCenterX']) > 0.2 and cars['cx'] > 100 and cars['cx'] < 300 and cars['cx'] < cars['prevCenterX']:
                leftCrossed += 1
                db.insert('0')
                cars['hasCrossed'] = True
                cars['beingTracked'] = False

    return leftCrossed

def ifCarsCrossedLineRight():
    rightCrossed = 0
    leftCrossed  = 0
    for index, cars in enumerate(blobs):
        if cars['beingTracked'] == True and cars['hasCrossed'] == False:
            print str(index) +': c ' + str(cars['cx']) + ' p ' + str(cars['prevCenterX'])
            if cars['prevCenterX'] != 0 and abs(cars['cx'] != cars['prevCenterX']) > 0.2 and cars['cx'] > 100 and cars['cx'] < 300 and cars['cx'] > cars['prevCenterX']:
                rightCrossed += 1
                db.insert('1')

                cars['hasCrossed'] = True
                cars['beingTracked'] = False

    return rightCrossed

def showCarsCount(countLeft, countRight):
    cv2.putText(img, str(countLeft), (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    cv2.putText(img, str(countRight), (250, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)


carsCount = 0

crossLineX1 = 220
crossLineY1 = 80
crossLineX2 = 220
crossLineY2 = 110

cascade_src = 'cars.xml'
video_src = 'video1.WMV'

car_cascade = cv2.CascadeClassifier(cascade_src)
i = 0

blobs = [{'x': 0, 'y': 0, 'w': 0, 'h': 0, 'cx': 0, 'cy': 0, 'beingTracked': False, 'newOrMatch': False, 'framesWithoutMatch': 0, 'prevCenterX': 0, 'prevCenterY': 0, 'hasCrossed': False}]

frameIndex = 0
leftCrossedCars = 0
rightCrossedCars = 0

db = mysql()

while True:
    try:
        pngs = glob.glob(r'web/webcam/images/*.png')
        # if os._exists(pngs[0]) == False:
        if cv2.waitKey(33) == 27:
            break

        if (len(pngs) < 1):
            continue

        img = cv2.imread(pngs[0])

        crop_img = img  # Crop from x, y, w, h -> 100, 200, 300, 400

        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 1)

        for (x, y, w, h) in cars:
            if x > 120 and x < 300 and y > 20 and y < 90:
                cx = x + (w / 2)
                cy = y + (h / 2)
                matchCurrentFrameCarsToExisting(x, y, w, h, cx, cy, frameIndex)

        showCars(frameIndex)
        leftCrossedCars += ifCarsCrossedLineLeft()
        rightCrossedCars += ifCarsCrossedLineRight()
        showCarsCount(leftCrossedCars, rightCrossedCars)
        cv2.imshow('video', img)
        os.remove(pngs[0])
        frameIndex += 1
        if cv2.waitKey(33) == 27:
            break

    except Exception, e:
        print 'got error ' + str(e)
        continue

cv2.destroyAllWindows()