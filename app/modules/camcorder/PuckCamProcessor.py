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
processMon = Monitoring(app_name='PuckCam', device_num='1', app_state='wait') # device_num=video_device


# Function returns the color of area based on the everaged colors of the ares
def determine_area_color(x1, x2, y1, y2, area, domination):
    # Calculate mean colors by each color channel
    blue = img[y1:y2, x1:x2, 0].mean()
    green = img[y1:y2, x1:x2, 1].mean()
    red = img[y1:y2, x1:x2, 2].mean()

    # Compare colors in the area to find red or blue domination
    if blue > red * domination:
        color = "blue"
    elif red > blue * domination:
        color = "red"
    else:
        color = "white"

    # Make a square around the area of the mean color
    img[y1:y1 + 1, x1:x2] = [blue, green, red]
    img[y2 - 1:y2, x1:x2] = [blue, green, red]
    img[y1:y2, x1:x1 + 1] = [blue, green, red]
    img[y1:y2, x2 - 1:x2] = [blue, green, red]

    # Write the identified color on the area
    cv2.putText(img, color, (x1, (y1 + y2) / 2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, 10)

    # Print out the results in text form
    logger.debug("Color of " + area + " area is " + color + ". (R:" + str(int(red)) + " G:" + str(int(green)) + " B:" +
                 str(int(blue)) + ")")
    # returm detected color
    return color

def img_processing(proc_mon, img):
    if is_sucessfully_read:
        # Let's read widht and hight of the image. If the size is always the same this can taken out to increase the speed
        img_h, img_w, layers = img.shape

        # Next variable regulates the widht from the left for floor color detection on the left
        brake_line_left = 50

        # The same for the right
        brake_line_right = img_w - 50

        # Next variable regulates the indent for floor color detection
        brake_line_indent = 15

        # calculate colors of left area.
        left_color = determine_area_color(brake_line_indent, brake_line_left, brake_line_indent, img_h / 2,
                                          "left", 1.3)

        # calculate colors of middle area.
        middle_color = determine_area_color(brake_line_left + 80, brake_line_right - 80, brake_line_indent,
                                            img_h / 2, "middle", 1.2)

        # calculate colors of right area.
        right_color = determine_area_color(brake_line_right, img_w - brake_line_indent, brake_line_indent,
                                           img_h / 2, "right", 1.3)

        # generate file name based on current time
        file_name = datetime.datetime.now().strftime(AppName + "_%Y%m%d_%H%M%S.%f") + '.png'

        proc_mon.set_processor_key(AppName, 'left_color', str(left_color))
        proc_mon.set_processor_key(AppName, 'middle_color', str(middle_color))
        proc_mon.set_processor_key(AppName, 'right_color', str(right_color))

        # Write the image to the file
        cv2.imwrite(os.path.join(full_path, file_name), img)
    else:
        logger.error(AppName + ' Cannot read video capture')
        processMon.set_processor_key(AppName, 'State', 'error')

# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    # Connect to video camera
    processMon.logger.info('Open video device num - ' + str(processMon.DeviceNum))
    PuckCamcorder = cv2.VideoCapture(processMon.DeviceNum)

    # Set some paramiters of capture webcam
    PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FPS, 5)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # PuckCamcorder.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :
        is_sucessfully_read = False

        # Grab a frame from the camera
        is_sucessfully_read, img = PuckCamcorder.read()

        # Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active':
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(processMon.AppName, 'StartPoint')
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, img)

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            processMon.create_file_storage(appstart_time_point)
            # State  iteration
            img_processing(processMon, img)
            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete


        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # And don't forget to release the camera!
    PuckCamcorder.release()
    processMon.set_app_state(state='stopped')
    processMon.logger.info('Stop application')

