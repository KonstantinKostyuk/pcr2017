#!/usr/bin/python

#  Import libraries
import math
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
    processMon.logger.info('Open device num - ' + str(processMon.DeviceNum))
    roboclaw = RoboClaw(processMon.DeviceNum, 0x80)
except:
    processMon.set_app_state(state='error')  # set and save


def calculate_position(logger, distance_mm, wheel_diameter, encoder_cpr):
    logger.debug('Function start')
    return int((distance_mm / (math.pi * wheel_diameter) * encoder_cpr))

def go_to_position(logger, enc_count):
    logger.debug('Function start')
    # go forward distance by encoders
    # roboclaw.SpeedAccelDeccelPositionM1M2(MC_ADDRESS, 5660, 5660, 5660, enc_count, 5660, 5660, 5660, enc_count, 0)
    roboclaw.drive_to_position_raw(motor=MotorLeft, accel=0, speed=0, deccel=0, position=enc_count, buffer=1)
    roboclaw.drive_to_position_raw(motor=MotorRight, accel=0, speed=0, deccel=0, position=enc_count, buffer=1)


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    processMon.logger.info('Start loop')

    isLoop = True
    while isLoop :
        # Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active':
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(processMon.AppName, 'StartPoint')
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration

            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # Finish
    processMon.set_processor_key(processMon.AppName, 'State', 'stopped')
    processMon.logger.info('Stop application')

