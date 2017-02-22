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

processMon = Monitoring(app_name='Global', device_num='', app_state='wait')


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :
        #Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active' or processMon.AppState == 'debug': # One time execution
            # get a main app start point
            appstart_time_point = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            processMon.logger.info('Define store dir - ' + appstart_time_point)
            processMon.create_file_storage(appstart_time_point)

            # init start time point
            processMon.logger.info('Set ' + processMon.AppName + '.StartPoint to ' + appstart_time_point)
            processMon.set_processor_key(processMon.AppName, 'StartPoint', appstart_time_point)

            # init Global values and save to storage
            processMon.set_processor_key(processMon.AppName, 'blue', 0)
            processMon.set_processor_key(processMon.AppName, 'red', 0)
            processMon.set_processor_key(processMon.AppName, 'BaseColor', 'blue')

            processMon.set_app_state(state='wait')

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # Finish
    processMon.set_app_state(state='stopped')
    processMon.logger.info('Stop application')
