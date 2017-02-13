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

AppName= 'LCD1602'
AppState = 'wait'
AppStateBefore = AppState

I2CBUS = 6                # Bus number for LCD


def print_to_lcd(procmon):
    lcdRed = procmon.get_processor_key(AppName, 'Red')
    lcdGreen = procmon.get_processor_key(AppName, 'Green')
    lcdBlue = procmon.get_processor_key(AppName, 'Blue')
    lcdLineA = procmon.get_processor_key(AppName, 'LineA')
    lcdLineB = procmon.get_processor_key(AppName, 'LineB')
    lcd.setColor(lcdRed, lcdGreen, lcdBlue)
    lcd.setCursor(0, 0)
    lcd.write(lcdLineA)
    lcd.setCursor(1, 0)
    lcd.write(lcdLineB)


# --- MAIN ---
if __name__ == '__main__':

    # get a main app start point
    appstart_time_point = str(sys.argv[1])

    # create logger with 'pcr2016'
    logger = logging.getLogger(AppName + 'Processor')
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

    # Set num of cam
    logger.info('Start app ' + AppName)

    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    # Connect to LCD
    logger.info('Open video device num - '+str(FrontCamDeviceNum))
    lcd = i2clcd.Jhd1313m1(I2CBUS, 0x3E, 0x62)

    # Set some paramiters
    myLcd.setCursor(0, 0)
    myLcd.setColor(0, 255, 255)

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + AppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to ' + AppState + ' for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)


    logger.info('Start capturing loop')
    isLoop = 1
    while isLoop == 1:

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active':
            print_to_lcd()

        elif AppState == 'debug':
            print_to_lcd()

        elif AppState == 'stopped': # if True exit from loop
            isLoop = 0


    # And don't forget to release the camera!
    FrontCamcorder.release()
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')
