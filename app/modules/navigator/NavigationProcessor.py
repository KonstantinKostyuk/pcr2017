#!/usr/bin/python

#  Import openCV libraries
import datetime
import math
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
from roboclaw.roboclaw import RoboClaw
# Complete load PCR modules

# --- Set global variables
#Used app names
GlobalAppName='Global'

MotorLeft = 1
MotorRight = 0

WheelDiameter = 90  # Diameter of wheel in mm
EncoderCPR = 3200   # Encoder CPR - Count Per Rotation

# --- Create global classes
processMon = Monitoring(app_name='Navigation', device_num='/dev/ttyACM0', app_state='wait')
try:
    # create to RoboClaw
    logger.info('Open device num - ' + str(DeviceNum))
    roboclaw = RoboClaw(DeviceNum, 0x80)
except:
    AppState = 'error'


def calculate_position(distance_mm, wheel_diameter, encoder_cpr):
    logger.debug('Function start')
    return int((distance_mm / (math.pi * wheel_diameter) * encoder_cpr))

def go_to_position(enc_count):
    logger.debug('Function start')
    # go forward distance by encoders
    # roboclaw.SpeedAccelDeccelPositionM1M2(MC_ADDRES, 5660, 5660, 5660, enc_count, 5660, 5660, 5660, enc_count, 0)
    roboclaw.drive_to_position_raw(motor=MotorLeft, accel=0, speed=0, deccel=0, position=enc_count, buffer=1)
    roboclaw.drive_to_position_raw(motor=MotorRight, accel=0, speed=0, deccel=0, position=enc_count, buffer=1)


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    logger.info('Set State to ' + AppState + ' for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)

    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)


        if AppState == 'active':
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(GlobalAppName, 'StartPoint')

            # Setup logging
            init_file_logging(logger, appstart_time_point)

            # Setup folder for data files
            logger.info('Define store dir - ' + appstart_time_point)
            processMon.create_file_storage(appstart_time_point)

        elif AppState == 'debug':
            AppState = 'wait'
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

        AppStateBefore = AppState

    # Finish
    processMon.set_processor_key(processMon.AppName, 'State', 'stopped')
    logger.info('Stop application')

