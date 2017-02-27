#!/usr/bin/python

#  Import openCV libraries
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
# Complete load PCR modules
from upm import pyupm_i2clcd as LCD

#Used app names
GlobalAppName='Global'

# --- Create global classes
processMon = Monitoring(app_name='LCD1602', device_num='6', app_state='wait') # I2C Bus number for LCD


def print_to_lcd(processor_mon, lcd1602):
    # get data from storage
    lcdRed = int(processor_mon.get_processor_key(processor_mon.AppName, 'Red'))
    lcdGreen = int(processor_mon.get_processor_key(processor_mon.AppName, 'Green'))
    lcdBlue = int(processor_mon.get_processor_key(processor_mon.AppName, 'Blue'))
    lcdLineA = processor_mon.get_processor_key(processor_mon.AppName, 'LineA')
    lcdLineB = processor_mon.get_processor_key(processor_mon.AppName, 'LineB')
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
    lcd = LCD.Jhd1313m1(processMon.DeviceNum, 0x3E, 0x62)

    # Set yellow
    lcd.setCursor(0, 0)
    lcd.setColor(255, 255, 0)

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
            print_to_lcd(processMon, lcd)

        elif processMon.AppState == 'debug':
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            print_to_lcd(processMon, lcd)
            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # Finish
    processMon.set_app_state(state='stopped')
    processMon.logger.info('Stop application')

