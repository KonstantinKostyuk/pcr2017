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


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    # Connect to video camera
    logger.info('Open video device num - ' + str(DeviceNum))
    FrontCamcorder = cv2.VideoCapture(DeviceNum)

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

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active' or AppState == 'debug':
            # get a main app start point
            appstart_time_point = str(sys.argv[1])
            init_file_logging(logger, appstart_time_point)
            logger.info('Define store dir - ' + appstart_time_point)
            processMon.create_file_storage(appstart_time_point)

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

        processMon.update_app_state_before()

    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_processor_key(processMon.AppName, 'State', 'stopped')
    logger.info('Stop application')

