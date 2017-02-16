#!/bin/bash

# testing script
~/pcr2017/app/modules/Global/GlobalProcessor.py &
sleep 2
~/pcr2017/app/modules/servo/ServoProcessor.py &
~/pcr2017/app/modules/camcorder/FrontCamProcessor.py &
~/pcr2017/app/modules/camcorder/PuckCamProcessor.py &
~/pcr2017/app/modules/LCD/LCD1602Processor.py &
~/pcr2017/app/modules/navigator/NavigationProcessor.py &

# flask server
~/pcr2017/run.py