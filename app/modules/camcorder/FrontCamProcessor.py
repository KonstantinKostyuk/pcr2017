#!/usr/bin/python

#  Import openCV libraries
import cv2
import datetime
import os
import sys
import logging
import redis
# Load PCR modules from ../
modules_path=os.path.dirname(sys.argv[0])
if len(modules_path) <= 1:  # 0 or 1 equal sterted from current dir
    modules_path=os.getcwd()+'/../'
else:                       # path
    modules_path=os.path.dirname(modules_path)
sys.path.append(modules_path)
from processors.monitoring import Monitoring
# Complete load PCR modules

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
    logger.info('Connect to processMon from FrontCamProcessor')
    processMon = Monitoring()
    logger.info('Set State to wait for FrontCamProcessor')
    processMon.set_processor_key(FrontCamAppName, 'State', 'wait')


    logger.info('Start capturing loop')
    while 1 == 1:
        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = FrontCamcorder.read()

        FrontCamAppState = processMon.get_processor_key(FrontCamAppName, 'State')
        if FrontCamAppState == 'active' or FrontCamAppState == 'debug':
            if is_sucessfully_read:
                # generate file name based on current time
                file_name = datetime.datetime.now().strftime(FrontCamAppName+"_%Y%m%d_%H%M%S.%f") + '.png'

                # Write the image to the file
                cv2.imwrite(os.path.join(full_path, file_name), img)
            else:
                logger.error("FRONT Cannot read video capture")
                processMon.set_processor_key(FrontCamAppName, 'State', 'error')

    # And don't forget to release the camera!

    FrontCamcorder.release()
    RedisServer.set(FrontCamAppName + '.State', 'stopped')
    logger.info('Stop application')

