#!/bin/bash

# testing script
~/pcr2017/app/modules/servo/ServoProcessor.py test &
~/pcr2017/app/modules/camcorder/FrontCamProcessor.py test &
~/pcr2017/app/modules/camcorder/PuckCamProcessor.py test &