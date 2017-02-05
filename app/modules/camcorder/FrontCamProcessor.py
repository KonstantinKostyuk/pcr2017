#!/usr/bin/python

#  Import openCV libraries
import cv2
import datetime
import os
import sys
import time
import logging
import redis

FrontCamDeviceNum = 0
FrontCamAppName='FrontCam'

# --- MAIN ---
if __name__ == '__main__':

    # get a main app start point
    appstart_time_point = str(sys.argv[1])

    # create logger with 'pcr2016'
    logger = logging.getLogger(FrontCamAppName+'Processor')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages, name based on appstart_time_point
    fh = logging.FileHandler(FrontCamAppName+appstart_time_point + '.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a debug log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(funcName)s(%(lineno)d)|%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Set num of cam
    logger.info('Start app '+FrontCamAppName)

    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    # Connect to video camera
    logger.info('Open front cam')
    FrontCamcorder = cv2.VideoCapture(FrontCamDeviceNum)

    # Set some paramiters of capture webcam
    FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

    # Set connection to REDIS
    logger.info('Connect to Redis from FrontCamProcessor')
    RedisServer = redis.StrictRedis(host='localhost', port=6379, db=0)
    RedisServer.set(FrontCamAppName+'.State', 'wait')


    logger.info('Start capturing loop')
    while 1 == 1:
        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = FrontCamcorder.read()

        FrontCamAppState = RedisServer.get(FrontCamAppName+'.State')
        if (is_sucessfully_read) and (FrontCamAppState != 'wait'):
            # generate file name based on current time
            file_name = datetime.datetime.now().strftime(FrontCamAppName+"_%Y%m%d_%H%M%S.%f") + '.png'

            # Write the image to the file
            cv2.imwrite(os.path.join(full_path, file_name), img)

        else:
            logger.error("FRONT Cannot read video capture")

    # And don't forget to release the camera!

    FrontCamcorder.release()
    RedisServer.set(FrontCamAppName + '.State', 'stopped')
    logger.info('Stop application')

