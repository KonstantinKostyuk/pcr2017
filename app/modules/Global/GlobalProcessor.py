#!/usr/bin/python

#  Import openCV libraries
import datetime
import os
import sys
import logging
import math
# Load PCR modules from ../
modules_path=os.path.dirname(sys.argv[0])
if len(modules_path) <= 1:  # 0 or 1 equal sterted from current dir
    modules_path=os.getcwd()+'/../'
else:                       # path
    modules_path=os.path.dirname(modules_path)
sys.path.append(modules_path)
from processors.monitoring import Monitoring
# Complete load PCR modules

DeviceNum = ''
AppName= 'Global'
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

    # Set num of cam
    init_console_logging(logger)
    logger.info('Start app ' + AppName)

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + AppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to ' + AppState + ' for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)

    logger.info('Start loop')
    isLoop = True
    while isLoop :

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active' or AppState == 'debug': # One time execution
            # get a main app start point
            appstart_time_point = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            # Setup logging
            init_file_logging(logger, appstart_time_point)

            # save start time point
            logger.info('Set ' + AppName + '.StartPoint to ' + appstart_time_point)
            processMon.set_processor_key(AppName, 'StartPoint', appstart_time_point)


            AppState = 'wait' # ToDo change to Navigate
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

    # Finish
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

