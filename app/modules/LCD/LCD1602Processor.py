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
# Complete load PCR modules
from upm import pyupm_i2clcd as i2clcd

DeviceNum = 6                # I2C Bus number for LCD
AppName= 'LCD1602'
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

def create_file_storage(appstart_time_point):
    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

def print_to_lcd(procmon, lcd1602):
    lcdRed = int(procmon.get_processor_key(AppName, 'Red'))
    lcdGreen = int(procmon.get_processor_key(AppName, 'Green'))
    lcdBlue = int(procmon.get_processor_key(AppName, 'Blue'))
    lcdLineA = procmon.get_processor_key(AppName, 'LineA')
    lcdLineB = procmon.get_processor_key(AppName, 'LineB')
    lcd1602.setColor(lcdRed, lcdGreen, lcdBlue)
    lcd1602.setCursor(0, 0)
    lcd1602.write(lcdLineA)
    lcd1602.setCursor(1, 0)
    lcd1602.write(lcdLineB)


# --- MAIN ---
if __name__ == '__main__':

    # Setup logging
    init_console_logging(logger)

    # Set num of cam
    logger.info('Start app ' + AppName)

    # Connect to LCD
    logger.info('Open I2C device num - ' + str(DeviceNum))
    lcd = i2clcd.Jhd1313m1(DeviceNum, 0x3E, 0x62)

    # Set yellow
    lcd.setCursor(0, 0)
    lcd.setColor(255, 255, 0)

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

        if AppState == 'active':
            # get a main app start point
            appstart_time_point = str(sys.argv[1])
            init_file_logging(logger, appstart_time_point)
            create_file_storage(appstart_time_point)

            print_to_lcd(processMon, lcd)

        elif AppState == 'debug':
            print_to_lcd(processMon, lcd)
            AppState = 'wait'
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

    # And don't forget to release the camera!
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

