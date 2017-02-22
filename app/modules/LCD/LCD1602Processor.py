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

# --- Create global classes
processMon = Monitoring(app_name='LCD1602', device_num='6', app_state='wait') # I2C Bus number for LCD


def print_to_lcd(procmon, lcd1602):
    # get data from storage
    lcdRed = int(procmon.get_processor_key(procmon.AppName, 'Red'))
    lcdGreen = int(procmon.get_processor_key(procmon.AppName, 'Green'))
    lcdBlue = int(procmon.get_processor_key(procmon.AppName, 'Blue'))
    lcdLineA = procmon.get_processor_key(procmon.AppName, 'LineA')
    lcdLineB = procmon.get_processor_key(procmon.AppName, 'LineB')
    # send data to LCD
    lcd1602.setColor(lcdRed, lcdGreen, lcdBlue)
    lcd1602.setCursor(0, 0)
    lcd1602.write(lcdLineA)
    lcd1602.setCursor(1, 0)
    lcd1602.write(lcdLineB)


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    # Connect to LCD
    processMon.logger.info('Open I2C device num - ' + str(processMon.DeviceNum))
    lcd = i2clcd.Jhd1313m1(processMon.DeviceNum, 0x3E, 0x62)

    # Set yellow
    lcd.setCursor(0, 0)
    lcd.setColor(255, 255, 0)

    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :

        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            processMon.logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active':
            # get a main app start point
            appstart_time_point = str(sys.argv[1])
            init_file_logging(processMon.logger, appstart_time_point)
            processMon.logger.info('Define store dir - ' + appstart_time_point)
            processMon.create_file_storage(appstart_time_point)

            print_to_lcd(processMon, lcd)

        elif AppState == 'debug':
            print_to_lcd(processMon, lcd)
            AppState = 'wait'
            processMon.set_processor_key(AppName, 'State', AppState)

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

    # And don't forget to release the camera!
    processMon.set_processor_key(processMon.AppName, 'State', 'stopped')
    processMon.logger.info('Stop application')

