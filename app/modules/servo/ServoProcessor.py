#!/usr/bin/python

#  Import  libraries
import time
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

#Used app names
ColorProcessorAppName='PuckCam'
NavigationAppName='Navigation'
GlobalAppName='Global'

#Current app name and settings
DeviceNum = '/dev/ttyACM1'
AppName= 'Servo'
AppState = 'wait'
AppStateBefore = AppState

# --- Create global classes
# create logger
logger = logging.getLogger(AppName + 'Processor')
try:
    # Connect to servo controller
    logger.info('Open device num - ' + str(DeviceNum))
    servo = ServoController(DeviceNum)
except:
    AppState = 'error'

GateState = 'close'
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


def get_color_list(procmon):
    colors = [procmon.get_processor_key(ColorProcessorAppName, 'left_color'),
              procmon.get_processor_key(ColorProcessorAppName, 'middle_color'),
              procmon.get_processor_key(ColorProcessorAppName, 'right_color')]
    return colors

def get_puck_color(procmon, list_colors):
    if list_colors[0] == list_colors[1] and list_colors[1] == list_colors[2]:
        procmon.set_processor_key(NavigationAppName, 'Base', list_colors[1])
        return 'none'
    elif list_colors[0] != list_colors[1] and list_colors[1] != list_colors[2]:
        procmon.set_processor_key(NavigationAppName, 'Base', 'white')
        return list_colors[1]
    else:
        procmon.set_processor_key(NavigationAppName, 'Base', 'white')
        return 'none'

def sort_pucks(puck_color, direction):
    if (puck_color == 'blue') and direction == 'FWD':
        # blue
        logger.info('Sort the ' +puck_color+ ' puck.')
        servo.setTarget(SRV_SEP_CHANEL, SEP_BLU_OPEN_POS)
        time.sleep(1)
        servo.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
        return puck_color
    elif (puck_color == 'red') and direction == 'FWD':
        # red
        logger.info('Sort the ' + puck_color + ' puck.')
        servo.setTarget(SRV_SEP_CHANEL, SEP_RED_OPEN_POS)
        time.sleep(1)
        servo.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
        return puck_color
    else:
        return 'none'

def release_red():
    logger.debug('Open RED gate')
    servo.setTarget(SRV_RED_CHANEL, GT_RED_OPEN_POS)

def release_blue():
    logger.debug('Open BLUE gate')
    servo.setTarget(SRV_BLU_CHANEL, GT_BLU_OPEN_POS)

def close_gates():
    logger.debug('Close gates')
    servo.setTarget(SRV_RED_CHANEL, SRV_NEUTRAL_POS)
    servo.setTarget(SRV_BLU_CHANEL, SRV_NEUTRAL_POS)

def active_iteration(proc_mon, gate_state_before):
    # Control separating
    list_colors = get_color_list(proc_mon)  # get list of colors from PuckCam
    puck_color = get_puck_color(proc_mon, list_colors)  # detect puck and color
    if puck_color != 'none':  # if not 'none' sorting
        sort_result = sort_pucks(puck_color, proc_mon.get_processor_key(NavigationAppName, 'Direction'))
        if sort_result != 'none':
            proc_mon.set_processor_key(GlobalAppName, sort_result,
                                         int(proc_mon.get_processor_key(GlobalAppName, sort_result)) + 1)

    # Control gates
    gate_state = proc_mon.get_processor_key(NavigationAppName, 'Gate')
    if gate_state_before != gate_state and gate_state == 'close':
        close_gates()
    elif gate_state_before != gate_state and gate_state == 'red':
        release_red()
    elif gate_state_before != gate_state and gate_state == 'blue':
        release_blue()
    return gate_state


# --- MAIN ---
if __name__ == '__main__':

    # get a main app start point
    appstart_time_point = str(sys.argv[1])

    # Setup logging
    init_console_logging(logger)
    init_file_logging(logger, appstart_time_point)

    # Set num of cam
    logger.info('Start app ' + AppName)

    # Dir for save
    current_dir = os.getcwd()
    store_dir = appstart_time_point
    full_path = os.path.join(current_dir, store_dir)
    logger.info('Define store dir full path: ' + full_path)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    try:
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
    except:
        AppState = 'error'

    # Set connection to REDIS
    logger.info('Connect to processMon from ' + AppName + 'Processor')
    processMon = Monitoring()
    logger.info('Set State to wait for ' + AppName + 'Processor')
    processMon.set_processor_key(AppName, 'State', AppState)

    logger.info('Start application loop')
    isLoop = True
    while isLoop :
        AppState = processMon.get_processor_key(AppName, 'State')
        if AppStateBefore != AppState:
            logger.info(AppName + 'Processor.State changed from ' + AppStateBefore + ' to ' + AppState)
            AppStateBefore = AppState

        if AppState == 'active': # active state start
            GateState = active_iteration(processMon, GateState)
            # active state complete

        elif AppState == 'debug': # debug state start
            GateState = active_iteration(processMon, GateState)
            processMon.set_processor_key(AppName, 'State', 'wait')
            # debug state complete

        elif AppState == 'stopped': # if True exit from loop
            isLoop = False

    # Close application
    processMon.set_processor_key(AppName, 'State', 'stopped')
    logger.info('Stop application')

