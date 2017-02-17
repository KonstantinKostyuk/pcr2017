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
processMon = Monitoring()


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

    # Set num of cam
    init_console_logging(logger)
    logger.info('Start app ' + AppName)

    # save state to storage
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
            create_file_storage(appstart_time_point)

            # init start time point
            logger.info('Set ' + AppName + '.StartPoint to ' + appstart_time_point)
            processMon.set_processor_key(AppName, 'StartPoint', appstart_time_point)

            # init Global values and save to storage
            processMon.set_processor_key(AppName, 'blue', 0)
            processMon.set_processor_key(AppName, 'red', 0)
            processMon.set_processor_key(AppName, 'BaseColor', 'blue')


            AppState = 'wait' #
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

    # Finish
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

