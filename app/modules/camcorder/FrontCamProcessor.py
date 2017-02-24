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


# --- Create global classes
processMon = Monitoring(app_name='FrontCam', device_num='0', app_state='wait')

def img_processing(proc_mon, img, is_sucessfully):
    if is_sucessfully:
        # generate file name based on current time
        file_name = datetime.datetime.now().strftime(proc_mon.AppName + "_%Y%m%d_%H%M%S.%f") + '.png'

        # Write the image to the file
        cv2.imwrite(os.path.join(full_path, file_name), img)
    else:
        proc_mon.logger.error(proc_mon.AppName + ' Cannot read video capture')
        processMon.set_processor_key(proc_mon.AppName, 'State', 'error')


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    # Connect to video camera
    processMon.logger.info('Open video device num - ' + str(processMon.processMon.DeviceNum))
    FrontCamcorder = cv2.VideoCapture(processMon.DeviceNum)

    # Set some paramiters of capture webcam
    FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)


    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :

        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = FrontCamcorder.read()

        # Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active':
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(processMon.AppName, 'StartPoint')
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, img, is_sucessfully_read)

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, img, is_sucessfully_read)
            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif AppState == 'stopped': # if True exit from loop
            isLoop = 0

        processMon.update_app_state_before()

    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_app_state(state='stopped')
    processMon.logger.info('Stop application')

