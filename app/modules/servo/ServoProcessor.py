#!/usr/bin/python

#  Import  libraries
import time
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
from Maestro.maestro import Controller as ServoController
# Complete load PCR modules

#Used app names
ColorProcessorAppName='PuckCam'
NavigationAppName='Navigation'
GlobalAppName='Global'

# --- Create global classes
processMon = Monitoring(app_name='Servo', device_num='/dev/ttyACM1', app_state='wait')
try:
    # Connect to Maestro controller
    processMon.logger.info('Open device num - ' + str(processMon.DeviceNum))
    Maestro = ServoController(processMon.DeviceNum)
except:
    processMon.set_app_state(state='error')  # set and save

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



def get_color_list(processor_mon):
    colors = [processor_mon.get_processor_key(ColorProcessorAppName, 'left_color'),
              processor_mon.get_processor_key(ColorProcessorAppName, 'middle_color'),
              processor_mon.get_processor_key(ColorProcessorAppName, 'right_color')]
    return colors


def get_puck_color(processor_mon, list_colors):
    if list_colors[0] == list_colors[1] and list_colors[1] == list_colors[2]:
        processor_mon.set_processor_key(NavigationAppName, 'Base', list_colors[1])
        return 'none'
    elif list_colors[0] != list_colors[1] and list_colors[1] != list_colors[2]:
        processor_mon.set_processor_key(NavigationAppName, 'Base', 'white')
        return list_colors[1]
    else:
        processor_mon.set_processor_key(NavigationAppName, 'Base', 'white')
        return 'none'


def sort_pucks(processor_mon, puck_color, direction):
    if (puck_color == 'blue') and direction == 'FWD':
        # blue
        processor_mon.logger.info('Sort the ' + puck_color + ' puck.')
        Maestro.setTarget(SRV_SEP_CHANEL, SEP_BLU_OPEN_POS)
        time.sleep(1)
        Maestro.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
        return puck_color
    elif (puck_color == 'red') and direction == 'FWD':
        # red
        processor_mon.logger.info('Sort the ' + puck_color + ' puck.')
        Maestro.setTarget(SRV_SEP_CHANEL, SEP_RED_OPEN_POS)
        time.sleep(1)
        Maestro.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
        return puck_color
    else:
        return 'none'


def release_red(processor_mon, servo):
    processor_mon.logger.debug('Open RED gate')
    servo.setTarget(SRV_RED_CHANEL, GT_RED_OPEN_POS)


def release_blue(processor_mon, servo):
    processor_mon.logger.debug('Open BLUE gate')
    servo.setTarget(SRV_BLU_CHANEL, GT_BLU_OPEN_POS)


def close_gates(processor_mon, servo):
    processor_mon.logger.debug('Close gates')
    servo.setTarget(SRV_RED_CHANEL, SRV_NEUTRAL_POS)
    servo.setTarget(SRV_BLU_CHANEL, SRV_NEUTRAL_POS)


def active_iteration(processor_mon, servo, gate_state_before):
    # Control separating
    list_colors = get_color_list(processor_mon)  # get list of colors from PuckCam
    puck_color = get_puck_color(processor_mon, list_colors)  # detect puck and color
    if puck_color != 'none':  # if not 'none' sorting
        sort_result = sort_pucks(processor_mon, puck_color, processor_mon.get_processor_key(NavigationAppName, 'Direction'))
        if sort_result != 'none':
            processor_mon.set_processor_key(GlobalAppName, sort_result,
                                         int(processor_mon.get_processor_key(GlobalAppName, sort_result)) + 1)

    # Control gates
    gate_state = processor_mon.get_processor_key(NavigationAppName, 'Gate')
    if gate_state_before != gate_state and gate_state == 'close':
        close_gates(processor_mon, servo)
    elif gate_state_before != gate_state and gate_state == 'red':
        release_red(processor_mon, servo)
    elif gate_state_before != gate_state and gate_state == 'blue':
        release_blue(processor_mon, servo)
    return gate_state


# --- MAIN ---
if __name__ == '__main__':

    # Start app
    processMon.logger.info('Start app ' + processMon.AppName)

    try:
        # init
        processMon.logger.info('Init CH: ' + str(SRV_SEP_CHANEL) +' POS: '+ str(SRV_NEUTRAL_POS))
        Maestro.setTarget(SRV_SEP_CHANEL, SRV_NEUTRAL_POS)
        Maestro.setAccel(SRV_SEP_CHANEL, ServoAccel)
        Maestro.setSpeed(SRV_SEP_CHANEL, ServoSpeed)
        processMon.logger.info('Init CH: ' + str(SRV_RED_CHANEL) + ' POS: ' + str(SRV_NEUTRAL_POS))
        Maestro.setTarget(SRV_RED_CHANEL, SRV_NEUTRAL_POS)
        Maestro.setAccel(SRV_RED_CHANEL, ServoAccel)
        Maestro.setSpeed(SRV_RED_CHANEL, ServoSpeed)
        processMon.logger.info('Init CH: ' + str(SRV_BLU_CHANEL) + ' POS: ' + str(SRV_NEUTRAL_POS))
        Maestro.setTarget(SRV_BLU_CHANEL, SRV_NEUTRAL_POS)
        Maestro.setAccel(SRV_BLU_CHANEL, ServoAccel)
        Maestro.setSpeed(SRV_BLU_CHANEL, ServoSpeed)
    except:
        processMon.set_app_state(state='error') # set and save

    processMon.logger.info('Start loop')
    isLoop = True
    while isLoop :

        #Get current state from Redis and update processMon.AppState
        processMon.get_app_state()

        if processMon.AppState == 'active': # active state start
            # get a main app start point
            appstart_time_point = processMon.get_processor_key(processMon.AppName, 'StartPoint')
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            GateState = active_iteration(processMon, Maestro, GateState)
            # active state complete

        elif processMon.AppState == 'debug': # debug state start
            # set a main app start point
            appstart_time_point = 'debug'
            # Setup logging
            processMon.init_file_logging(appstart_time_point)
            full_path = processMon.create_file_storage(appstart_time_point)
            # State  iteration
            GateState = active_iteration(processMon, Maestro, GateState)
            # Change state to wait
            processMon.set_app_state(state='wait')
            # debug state complete

        elif processMon.AppState == 'stopped': # if True exit from loop
            isLoop = False

        processMon.update_app_state_before()

    # Finish
    processMon.set_app_state(state='wait')
    processMon.logger.info('Stop application')

