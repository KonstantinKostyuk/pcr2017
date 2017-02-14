#!/bin/bash

# testing script
~/pcr2017/app/modules/servo/ServoProcessor.py test &
~/pcr2017/app/modules/camcorder/FrontCamProcessor.py test &
~/pcr2017/app/modules/camcorder/PuckCamProcessor.py test &
~/pcr2017/app/modules/LCD/LCD1602Processor.py test &
~/pcr2017/app/modules/navigator/NavigationProcessor.py test &

# flask server
~/pcr2017/run.py