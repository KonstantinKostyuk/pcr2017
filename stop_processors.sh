#!/bin/bash

# stop All processors use Redis storage
redis-cli set LCD1602.State stopped
redis-cli set FrontCam.State stopped
redis-cli set PuckCam.State stopped
redis-cli set Servo.State stopped
redis-cli set Navigation.State stopped