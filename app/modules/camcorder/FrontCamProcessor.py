#!/usr/bin/python

#  Import openCV libraries
import cv2
import datetime
import os
import sys
# Load PCR modules from ../
modules_path=os.path.dirname(sys.argv[0])
if len(modules_path) <= 1:  # 0 or 1 equal started from current dir
    modules_path=os.getcwd()+'/../'
else:                       # path
    modules_path=os.path.dirname(modules_path)
sys.path.append(modules_path)
from processors.monitoring import Monitoring
# Complete load PCR modules


# --- Create global classes
processMon = Monitoring(app_name='FrontCam', device_num='0', app_state='wait')

def img_processing(processor_mon, img, is_sucessfully, full_path):
    if is_sucessfully:
        # generate file name based on current time
        file_name = datetime.datetime.now().strftime(processor_mon.AppName + "_%Y%m%d_%H%M%S.%f") + '.png'

        # Write the image to the file
        cv2.imwrite(os.path.join(full_path, file_name), img)
    else:
        processor_mon.logger.error(processor_mon.AppName + ' Cannot read video capture')
        processMon.set_processor_key(processor_mon.AppName, 'State', 'error')


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    # Connect to video camera
    processMon.logger.info('Open video device num - ' + str(processMon.DeviceNum))
    FrontCamcorder = cv2.VideoCapture(int(processMon.DeviceNum))

    # Set some parameters of capture webcam
    FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # FrontCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)


    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :

        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, image = FrontCamcorder.read()

        # Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active':
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(processMon.AppName, 'StartPoint')
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path_to_storage = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, image, is_sucessfully_read, full_path_to_storage)

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path_to_storage = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, image, is_sucessfully_read, full_path_to_storage)
            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = 0

        processMon.update_app_state_before()

    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_app_state(state='stopped')
    processMon.logger.info('Stop application')

