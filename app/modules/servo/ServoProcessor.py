#!/usr/bin/python

#  Import openCV libraries
import cv2
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
from Maestro.maestro import Controller as ServoController
# Complete load PCR modules

ServoControllerDeviceNum = 1
ServoAppName= 'Setvo'
ServoSpeed=0 # Unlimited by SW, as speed as possible
ServoAccel=0 # Unlimited by SW, as speed as possible

SRV_SEP_CHANEL = 0 # Chanel 0 - Separator
SRV_RED_CHANEL = 1 # Chanel 1 - Red storage gate
SRV_BLU_CHANEL = 2 # Chanel 2 - Blue storage gate

SRV_NEUTRAL_POS = 6000   # Neutral position for all servos
SEP_RED_OPEN_POS = 9000  # Separator sort to RED
SEP_BLU_OPEN_POS = 3000  # Separator sort to BLUE
GT_RED_OPEN_POS = 4000   # Gate for RED store open
GT_BLU_OPEN_POS = 8000   # Gate for BLUE store open

# --- MAIN ---
if __name__ == '__main__':

    # get a main app start point
    appstart_time_point = str(sys.argv[1])

    # create logger with 'pcr2016'
    logger = logging.getLogger(ServoAppName + 'Processor')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages, name based on appstart_time_point
    fh = logging.FileHandler(ServoAppName + appstart_time_point + '.log')
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
    logger.info('Start app ' + ServoAppName)

    # Dir for save cam frames
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    # Connect to servo controller
    logger.info('Open device num - ' + str(ServoControllerDeviceNum))
    servo = ServoController(ServoControllerDeviceNum)
    logger.info('Init CH: ' + str(SRV_SEP_CHANEL) +' POS: '+ str(SRV_NEUTRAL_POS))
    servo.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
    servo.setAccel(SRV_SEP_CHANEL, ServoAccel)
    servo.setSpeed(SRV_SEP_CHANEL, ServoSpeed)
    logger.info('Init CH: ' + str(SRV_RED_CHANEL) + ' POS: ' + str(SRV_NEUTRAL_POS))
    servo.setTarget(SRV_RED_CHANEL, SRV_NEUTRAL_POS)
    servo.setAccel(SRV_RED_CHANEL, ServoAccel)
    servo.setSpeed(SRV_RED_CHANEL, ServoSpeed)
    logger.info('Init CH: ' + str(SRV_BLU_CHANEL) + ' POS: ' + str(SRV_NEUTRAL_POS))
    servo.setTarget(SRV_BLU_CHANEL, SRV_NEUTRAL_POS)
    servo.setAccel(SRV_BLU_CHANEL, ServoAccel)
    servo.setSpeed(SRV_BLU_CHANEL, ServoSpeed)

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + ServoAppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to wait for ' + ServoAppName + 'Processor')
    AppState = 'wait'
    AppStateBefore = AppState
    processMon.set_processor_key(ServoAppName, 'State', AppState)


    logger.info('Start application loop')
    isLoop = 1
    while isLoop == 1:
        AppState = processMon.get_processor_key(ServoAppName, 'State')
        if AppStateBefore != AppState:
            logger.info(ServoAppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active' or AppState == 'debug':
            time.sleep(1)  #ToDo add servo actions
        elif AppState == 'stopped': # if True exit from loop
            isLoop = 0

    # Close application
    processMon.set_processor_key(ServoAppName, 'State', 'stopped')
    logger.info('Stop application')

