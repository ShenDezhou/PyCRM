import redis

# Redis Key

# hash object
OVERALL_CAPACITY = 'capacity'
VOLUME_STATUS = 'status'
VOLUME_USAGE = 'usage'
VOLUME_PREFIX = 'volume:'
SNAPSHOT_PREFIX = 'snapshot:'
BRICK_PREFIX = 'brick:'
VOLUME_NFS = 'nfs'
VOLUME_SAMBA = 'samba'
VOLUME_ISCSI = 'iscsi' 
VOLUME_SWIFT = 'swift'

# set object
VOLUME_NAMES = 'volume:names'
NETWORKIO_IN = 'network_io_in:names'
NETWORKIO_OUT = 'network_io_out:names'


# single object
CLUSTER_DISKS = 'cluster:disks'
CLUSTER_LIST = 'cluster:list'
CLUSTER_RESOURCE = 'cluster:resource'

CLUSTER_DEVICE = 'cluster:devices'
# list object
MEMORY_USAGE_PREFIX = 'memory_usage:'  # memory_usage:192.168.1.150
CPU_USAGE_PREFIX = 'cpu_usage:'  # cpu_usage:192.168.1.150:1 cpu_usage:192.168.1.150:2 etc
READ_SPEED_PREFIX = 'read_speed:'
WRITE_SPEED_PREFIX = 'write_speed:'
DISKWRITE = 'diskio_write:'
DISKREAD = 'diskio_read:'
DISKWRITEALL = 'disk_writes:'
DISKREADALL = 'disk_reads:'
DISK_NAME_WRITE = 'disk_name_write:'
DISK_NAME_READ = 'diskname_read:'
NETWORKIO_NAME_IN_INIT = 'network_machine_in_init:'
NETWORKIO_NAME_OUT_INIT = 'network_machine_out_init:'
NETWORKIO_IN_SUM_INIT = 'networkio_in_sum_init:'
NETWORKIO_OUT_SUM_INIT = 'networkio_out_sum_init:'

TIMESTAMP = 'timestamp:'

# Redis Value
VOLUME_STATUS_STARTED = 'Started'
VOLUME_STATUS_STOPPED = 'Stopped'
VOLUME_CAPACITY = 'capacity'
VOLUME_USAGE = 'usage'
TIME = "time"
DATA = "data"
VIEW_MONITOR="VIEW_MONITOR"
MONITOR_VIEW="MONITOR_VIEW"

# This class is wrapper for a redis instance
class Redis:
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    @staticmethod
    def set(name, value):
        Redis.r.set(name, value)

    @staticmethod
    def psetex(name, time, value):
        Redis.r.psetex(name, time, value)

    @staticmethod
    def setex(name, time, value):
        Redis.r.setex(name, time, value)

    @staticmethod
    def pttl(name):
        Redis.r.pttl(name)

    @staticmethod
    def ttl(name):
        Redis.r.ttl(name)

    @staticmethod
    def get(name):
        return Redis.r.get(name)

    @staticmethod
    def delete(name):
        Redis.r.delete(name)

    @staticmethod
    def hset(name, key, value):
        Redis.r.hset(name, key, value)

    @staticmethod
    def hmset(name, mapping):
        Redis.r.hmset(name, mapping)

    @staticmethod
    def hget(name, key):
        return Redis.r.hget(name, key)

    @staticmethod
    def hgetall(name):
        return Redis.r.hgetall(name)

    @staticmethod
    def sadd(name, value):
        Redis.r.sadd(name, value)

    @staticmethod
    def sget(name):
        return Redis.r.smembers(name)

    @staticmethod
    def srem(name, key):
        return Redis.r.srem(name, key)

    @staticmethod
    def lrem(name, value,num):
        Redis.r.lrem(name, value,num)

    # append to list
    @staticmethod
    def lpush(name, key):
        Redis.r.lpush(name, key)

    @staticmethod
    def lpop(name):
        return Redis.r.lpop(name)

    @staticmethod
    def blpop(name):
        return Redis.r.blpop(name)

    @staticmethod
    def rpush(name, key):
        Redis.r.rpush(name, key)

    @staticmethod
    def rpop(name):
        return Redis.r.rpop(name)



    
