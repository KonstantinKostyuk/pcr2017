#!/usr/bin/python

#  Import openCV libraries
import cv2
import datetime
import os
import sys
import logging
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
    logger.info('Open video device num - '+str(FrontCamDeviceNum))
    FrontCamcorder = cv2.VideoCapture(FrontCamDeviceNum)

    # Set some paramiters of capture webcam
    FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

    # Set connection to REDIS
    logger.info('Connect to processMon from '+FrontCamAppName+'Processor')
    processMon = Monitoring()
    logger.info('Set State to wait for '+FrontCamAppName+'Processor')
    FrontCamAppState = 'wait'
    FrontCamAppStateBefore = FrontCamAppState
    processMon.set_processor_key(FrontCamAppName, 'State', FrontCamAppState)


    logger.info('Start capturing loop')
    isLoop = 1
    while isLoop == 1:
        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = FrontCamcorder.read()

        FrontCamAppState = processMon.get_processor_key(FrontCamAppName, 'State')
        if FrontCamAppStateBefore != FrontCamAppState:
            logger.info(FrontCamAppName + 'Processor.State changed from ' + FrontCamAppStateBefore + ' to ' + FrontCamAppState)
            FrontCamAppStateBefore = FrontCamAppState

        if FrontCamAppState == 'active' or FrontCamAppState == 'debug':
            if is_sucessfully_read:
                # generate file name based on current time
                file_name = datetime.datetime.now().strftime(FrontCamAppName+"_%Y%m%d_%H%M%S.%f") + '.png'

                # Write the image to the file
                cv2.imwrite(os.path.join(full_path, file_name), img)
            else:
                logger.error(FrontCamAppName + ' Cannot read video capture')
                processMon.set_processor_key(FrontCamAppName, 'State', 'error')
        elif FrontCamAppState == 'stopped': # if True exit from loop
            isLoop = 0


    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_processor_key(FrontCamAppName, 'State', 'stopped')
    logger.info('Stop application')

