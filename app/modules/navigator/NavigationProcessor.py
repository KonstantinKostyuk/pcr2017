#!/usr/bin/python

import os
import sys
# Load PCR modules from ../
modules_path=os.path.dirname(sys.argv[0])
if len(modules_path) <= 1:  # 0 or 1 equal sterted from current dir
    modules_path=os.getcwd()+'/../'
else:                       # path
    modules_path=os.path.dirname(modules_path)
sys.path.append(modules_path)
from processors.monitoring import Monitoring
# Complete load PCR modules

processMon = Monitoring()
processMon.set_processor_key('Navigation', 'State', 'debug')

print processMon.get_processor_redis('Navigation')
time.sleep(120)
