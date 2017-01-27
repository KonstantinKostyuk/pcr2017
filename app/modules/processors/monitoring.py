import subprocess

class Monitoring:
    def __init__(self):
        self.RedisDataStorageCLI='/usr/bin/redis-cli'
        self.RedisCmdPing='ping'

    def get_redis_state(self):
        cmd=self.RedisDataStorageCLI + ' ' + self.RedisCmdPing
        pipe = subprocess.PIPE
        p = subprocess.Popen(cmd, shell=True, stdout=pipe, stderr=subprocess.STDOUT, close_fds=True)
        if p.stdout.read().startswith('PONG') :
            return 0 #OK
        else:
            return 1 #NOK

if __name__ == '__main__':
    processMon = Monitoring()
    print( processMon.get_redis_state() )
