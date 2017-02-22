import subprocess
import logging
import psutil
import redis
import os


class Monitoring:
    def __init__(self, app_name, device_num, app_state = 'wait'):
        # Redis variables
        self.RedisDataStorageCLI='/usr/bin/redis-cli'
        self.RedisCmdPing='ping'

        # Redis server check state and create connection
        if self.get_redis_state() == 0:
            self.RedisState = 0
            self.RedisServer = redis.StrictRedis(host='localhost', port=6379, db=0)

        # Application variables
        self.DeviceNum = device_num
        self.AppName = app_name
        self.AppState = app_state
        self.AppStateBefore = self.AppState

        # global logger object
        self.logger = logging.getLogger(self.AppName + 'Processor')
        self.init_console_logging()
        self.isFHLogging = False

        # save state to storage
        self.logger.info('Set State to ' + self.AppState + ' for ' + self.AppName + 'Processor')
        self.save_app_state()

    '''
    Update application old state
    '''
    def update_app_state_before(self):
        self.AppStateBefore = self.AppState

    '''
    Save application state to Redis
    '''
    def save_app_state(self):
        self.set_processor_key(self.AppName, 'State', self.AppState)


    def set_app_state(self, state='wait'):
        if self.AppState != state:
            self.logger.info(self.AppName + 'Processor.State changed from ' + self.AppState + ' to ' + state)
            self.AppState = state
            self.save_app_state()

    def get_app_state(self):
        self.set_app_state(state = self.get_processor_key(self.AppName, 'State'))
        return self.AppState


    '''
    Init application console logging handler
    '''
    def init_console_logging(self):
        # setup logger level
        self.logger.setLevel(logging.DEBUG)

        # create console handler with a debug log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(funcName)s(%(lineno)d)|%(message)s')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(ch)


    '''
    Init application file  logging handler
    '''
    def init_file_logging(self, appstart_time_point):

        if self.isFHLogging == False:
            # setup logger level
            self.logger.setLevel(logging.DEBUG)

            # create file handler which logs even debug messages, name based on appstart_time_point
            fh = logging.FileHandler(self.AppName+'-'+ appstart_time_point + '.log')
            fh.setLevel(logging.DEBUG)

            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(funcName)s(%(lineno)d)|%(message)s')
            fh.setFormatter(formatter)

            # add the handlers to the logger
            self.logger.addHandler(fh)

            self.isFHLogging = True


    '''
    function to check - is REDIS server active and response
    0 - OK active
    1 - NOK not response
    '''
    def get_redis_state(self):
        cmd=self.RedisDataStorageCLI + ' ' + self.RedisCmdPing
        pipe = subprocess.PIPE
        p = subprocess.Popen(cmd, shell=True, stdout=pipe, stderr=subprocess.STDOUT, close_fds=True)
        if p.stdout.read().startswith('PONG') :
            return 0 #OK
        else:
            return 1 #NOK

    '''
    function to check - is process started
    '''
    def get_processor_state(self, name):
        for process in psutil.process_iter():
            if str(process.name()).startswith(name):
                return 0 #OK process active
        return 1 #NOK process not active

    '''
    function to return state for current name
    '''
    def get_processor_redis(self, name):
        if self.get_processor_state(name) == 0:
            return self.RedisServer.get(name+'.State')
        else:
            self.RedisServer.set(name+'.State', 'stopped')
            return 'stopped'

    '''
    function return any value from key for processor
    '''
    def get_processor_key(self, prcessor, key):
        return self.RedisServer.get(prcessor +'.'+ key)

    '''
    function return any value from key for processor
    '''
    def set_processor_key(self, prcessor, key, value):
        return self.RedisServer.set(prcessor + '.' + key, value)

    '''
    function create  directory for save any information
    '''
    def create_file_storage(self, appstart_time_point):
        self.logger.info('Define store dir - ' + appstart_time_point)
        current_dir = os.getcwd()
        store_dir = appstart_time_point
        full_path = os.path.join(current_dir, store_dir)
        # logger.info('Define store dir full path: ' + full_path)
        if not os.path.exists(full_path):
            os.mkdir(full_path)

if __name__ == '__main__':
    processMon = Monitoring()
    print( 'Redis server state (0=worked) ' + str(processMon.get_redis_state()) )
    print( 'Process "redis-server" state (0=worked) ' + str(processMon.get_processor_state('redis-server')) )
    print( '---' )
    print( 'Process "NavigationProcessor" state (0=worked) ' + str(processMon.get_processor_state('Navigation')) )
    print( 'Process "ServoProcessor" state (0=worked) ' + str(processMon.get_processor_state('Servo')) )
    print( 'Process "PuckCamProcessor" state (0=worked) ' + str(processMon.get_processor_state('PuckCam')) )
    print( 'Process "FrontCamProcessor" state (0=worked) ' + str(processMon.get_processor_state('FrontCam')))
    print('---')
    print( 'Process "NavigationProcessor" Redis.State ' + str(processMon.get_processor_redis('Navigation')))
#    print( 'Process "ServoProcessor" state (0=worked) ' + str(processMon.get_processor_redis('Servo')) )
#    print( 'Process "PuckCamProcessor" state (0=worked) ' + str(processMon.get_processor_redis('PuckCam')) )
    print( 'Process "FrontCamProcessor" state (0=worked) ' + processMon.get_processor_redis('FrontCam'))

    processMon.create_file_storage('AA-A2-A3')