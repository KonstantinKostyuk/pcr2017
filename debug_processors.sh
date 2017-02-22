#!/bin/bash

# stop All processors use Redis storage
regis-cli set Global.State debug
redis-cli set LCD1602.State debug
redis-cli set FrontCam.State debug
redis-cli set PuckCam.State debug
redis-cli set Servo.State debug
redis-cli set Navigation.State debug
