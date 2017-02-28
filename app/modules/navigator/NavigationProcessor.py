#!/usr/bin/python

#  Import libraries
import math
import time
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
MotorRight = 2

WheelDiameter = 90  # Diameter of wheel in mm
EncoderCPR = 3200   # Encoder CPR - Count Per Rotation

# Polygon size
FieldLength = 2500  # mm
BaseLength  = 700   # mm
# Robot size
RobotLength = 380   # mm
RobotWidth  = 370   # mm
RobotBaseWidth = 306 # mm
FrontBaseLength = 115   # mm
BackBaseLength = 265    # mm



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


def wait_position(logger, l_enc_count, r_enc_count, time_sec, enc_count_tolerance):
    logger.debug('Function start')
    left_tolerance = (l_enc_count / 100) * enc_count_tolerance
    right_tolerance = (r_enc_count / 100) * enc_count_tolerance
    current_time = time.time()
    isContinue = True
    while isContinue :
        now = time.time()
        if (now - current_time) >= time_sec:
            isContinue = False
        left = roboclaw.read_encoder(MotorLeft)
        if (l_enc_count - left) <= left_tolerance :
            isContinue = False
        right = roboclaw.read_encoder(MotorLeft)
        if (r_enc_count - right) <= right_tolerance:
            isContinue = False
            


def go_to_position(logger, enc_count, l_accel=0, l_speed=0, l_deccel=0, r_accel=0, r_speed=0, r_deccel=0):
    logger.debug('Function start')
    # go forward distance by encoders
    # roboclaw.SpeedAccelDeccelPositionM1M2(MC_ADDRESS, 5660, 5660, 5660, enc_count, 5660, 5660, 5660, enc_count, 0)
    roboclaw.drive_to_position_raw(motor=MotorLeft, accel=l_accel, speed=l_speed, deccel=l_deccel, position=enc_count, buffer=1)
    roboclaw.drive_to_position_raw(motor=MotorRight, accel=r_accel, speed=r_speed, deccel=r_deccel, position=enc_count, buffer=1)


def release_pucks_to_base(processor_mon, field_base_color):
    processor_mon.logger.debug('Function start')
    # check base
    # field_base_color = processor_mon.get_processor_key(processor_mon.AppName, 'Base')

    if field_base_color == processor_mon.get_processor_key(GlobalAppName, 'BaseColor'):
        processor_mon.get_processor_key(processor_mon.AppName, 'Gate', field_base_color)
        position_enc_count = calculate_position(processor_mon.logger, BaseLength, WheelDiameter, EncoderCPR)

        # go forward
        processor_mon.set_processor_key(processor_mon.AppName, 'Direction', 'FWD')
        go_to_position(processor_mon.logger, position_enc_count, 5660, 5660, 5660, 5660, 5660, 5660)
        wait_position(processor_mon.logger, position_enc_count, position_enc_count, 2, 10)

        # go back
        processor_mon.get_processor_key(processor_mon.AppName, 'Gate', 'close')
        processor_mon.set_processor_key(processor_mon.AppName, 'Direction', 'BWD')
        go_to_position(processor_mon.logger, 1, 5660, 5660, 5660, 5660, 5660, 5660)
        wait_position(processor_mon.logger, 1, 1, 2, 10)


def single_shuttle_drive(processor_mon):
    processor_mon.logger.debug('Function start')
    processor_mon.set_processor_key(processor_mon.AppName, 'Direction', 'FWD')
    position_enc_count = calculate_position(processor_mon.logger, FieldLength - RobotLength, WheelDiameter, EncoderCPR)

    #go forward
    go_to_position(processor_mon.logger, position_enc_count, 5660, 5660, 5660, 5660, 5660, 5660)
    wait_position(processor_mon.logger, position_enc_count, position_enc_count, 2, 10)

    # go back
    processor_mon.set_processor_key(processor_mon.AppName, 'Direction', 'BWD')
    go_to_position(processor_mon.logger, 1, 5660, 5660, 5660, 5660, 5660, 5660)
    wait_position(processor_mon.logger, 1, 1, 2, 10)


def active_iteration(processor_mon):
    single_shuttle_drive(processor_mon)
    release_pucks_to_base(processor_mon, processor_mon.get_processor_key(processor_mon.AppName, 'Base'))



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
            active_iteration(processMon)

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            active_iteration(processMon)

            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # Finish
    processMon.set_processor_key(processMon.AppName, 'State', 'stopped')
    processMon.logger.info('Stop application')

