import subprocess
import psutil
import redis


class Monitoring:
    def __init__(self):
        self.RedisDataStorageCLI='/usr/bin/redis-cli'
        self.RedisCmdPing='ping'

        if self.get_redis_state() == 0:
            self.RedisState = 0
            self.RedisServer = redis.StrictRedis(host='localhost', port=6379, db=0)


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
        for proc in psutil.process_iter():
            if str(proc.name()).startswith(name):
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
