#!/usr/bin/python

#  Import openCV libraries
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
from roboclaw.roboclaw import RoboClaw
# Complete load PCR modules

DeviceNum = '/dev/ttyACM0'
AppName= 'Navigation'
AppState = 'wait'
AppStateBefore = AppState

# create logger
logger = logging.getLogger(AppName + 'Processor')

def init_logging(logger):
    # setup logger level
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages, name based on appstart_time_point
    fh = logging.FileHandler(AppName + appstart_time_point + '.log')
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

# --- MAIN ---
if __name__ == '__main__':

    # Setup logging
    init_logging(logger)

    # get a main app start point
    appstart_time_point = str(sys.argv[1])

    # Set num of cam
    logger.info('Start app ' + AppName)

    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    # Connect to RoboClaw
    logger.info('Open device num - '+str(DeviceNum))
    roboclaw = RoboClaw(DeviceNum, 0x80)

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + AppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to ' + AppState + ' for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)

    logger.info('Start loop')
    isLoop = 1
    while isLoop == 1:

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active':
            AppState = 'wait' # ToDo change to Navigate
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'debug':
            AppState = 'wait'
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = 0

    # Finish
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

