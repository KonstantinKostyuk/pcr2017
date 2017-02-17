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

DeviceNum = 0
AppName= 'FrontCam'
AppState = 'wait'
AppStateBefore = AppState

# create logger
logger = logging.getLogger(AppName + 'Processor')

def init_console_logging(logger):
    # setup logger level
    logger.setLevel(logging.DEBUG)

    # create console handler with a debug log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(funcName)s(%(lineno)d)|%(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)


def init_file_logging(logger, appstart_time_point):
    # setup logger level
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages, name based on appstart_time_point
    fh = logging.FileHandler(AppName + appstart_time_point + '.log')
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(funcName)s(%(lineno)d)|%(message)s')
    fh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)

def create_file_storage(appstart_time_point):
    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

# --- MAIN ---
if __name__ == '__main__':

    # Setup logging
    init_console_logging(logger)

    # Set num of cam
    logger.info('Start app ' + AppName)

    # Connect to video camera
    logger.info('Open video device num - ' + str(DeviceNum))
    FrontCamcorder = cv2.VideoCapture(DeviceNum)

    # Set some paramiters of capture webcam
    FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + AppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to wait for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)


    logger.info('Start capturing loop')
    isLoop = 1
    while isLoop == 1:
        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = FrontCamcorder.read()

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active' or AppState == 'debug':
            # get a main app start point
            appstart_time_point = str(sys.argv[1])
            init_file_logging(logger, appstart_time_point)
            create_file_storage(appstart_time_point)

            if is_sucessfully_read:
                # generate file name based on current time
                file_name = datetime.datetime.now().strftime(AppName + "_%Y%m%d_%H%M%S.%f") + '.png'

                # Write the image to the file
                cv2.imwrite(os.path.join(full_path, file_name), img)
            else:
                logger.error(AppName + ' Cannot read video capture')
                processMon.set_processor_key(AppName, 'State', 'error')
        elif AppState == 'stopped': # if True exit from loop
            isLoop = 0


    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

