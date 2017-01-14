from command_execute import *
from redis_util import *
import simplejson as json
from time import sleep
import time
import re
from snmp import snmp_query
from config import CONFIG_LOCAL_HOST, CONFIG_DISK_PREFIX, CONFIG_QUERY_PERIOD
from check_util import none, empty
import logging
import sys


# COMMAND CONSTANT
TRANSPORT_TYPE =' transport tcp '
VOLUME_CREATE = 'gluster volume create '
DISPERSE_40 = ' disperse 40 redundancy 8 '
DISPERSE_48 = ' disperse 48 redundancy 16 '
VOLUME_DELETE = 'gluster volume delete '
VOLUME_STOP = 'gluster volume stop '
VOLUME_START = 'gluster volume start '
VOLUME_QUOTA = 'gluster volume quota '
VOLUME_QUOTA_LIMIT_USAGE = ' limit-usage / '
VOLUME_QUOTA_LIST = ' list / '
VOLUME_SET = 'gluster volume set '
SNAPSHOT_CREATE = 'gluster snapshot create '
SNAPSHOT_DELETE = 'gluster snapshot delete '
SNAPSHOT_INFO = 'gluster snapshot info volume '
SNAPSHOT_RESOTRE = 'gluster snapshot restore '
PEER_PROBE = 'gluster peer probe '
PEER_DETACH = 'gluster peer detach '
PEER_STATUS = 'gluster peer status'
VOLUME_TOP = 'gluster volume top '
WRITE_PERF = ' write-perf list-cnt 20'
READ_PERF = ' read-perf list-cnt 20'
FORCE = ' force'
ENABLE = ' enable'
GB = 'GB'
DHT_NUM = 4

GLUSTERD_RESTART = 'systemctl restart glusterd.service'
# LSBLK = 'lsblk'

# used for test
DISPERSE__3_1 = ' disperse 4 redundancy 1 '
DISPERSE__4_2 = ' disperse 6 redundancy 2 '

# To do:log in file
cur_node_index = 0
BRICK_PER_NODE = 12
# BRICK_PER_NODE = 2
# <hostname : current brick index>
cur_brick_record = dict()


def num2percent(num):
    return str(round(num * 100, 2))


def kb2gb(num):
    return str(round(num / 1048576, 1))


def refresh_createvolume_status(volume_name='all'):
    success, result, volume_stop = execute_volume_status(volume_name)
    if success:
        volume_running = list()
        for volume in result:
            volume_name = volume['Status of volume'].strip()
            # volume_name is volume's name who is running
            volume_running.append(volume_name)
            bricks = list()
            total_used = 0

            # set volume's brick list
            for brick in volume['bricks']:
                brick_name = brick['Brick']
                l_index = brick_name.find(' ')
                address = brick_name[l_index:].strip()
        str_free = brick['Disk Space Free'][:-2]
        str_total = brick['Total Disk Space'][:-2]
        if str_free is not None and str_total is not None:
            free = float(str_free)
            total = float(str_total)
            total_used += total - free
            usage = num2percent((1 - free / total))
            brick_state = brick['Online']
            brick = {"address": address, "online": brick_state, "usage": usage}
            bricks.append(brick)
            Redis.set(BRICK_PREFIX + volume_name, json.dumps(bricks))
            # add volume name to name-set
            Redis.sadd(VOLUME_NAMES, volume_name)

            # set volume info for volume created manually
            volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)
            if empty(volume_info) or VOLUME_NFS not in volume_info:
                Redis.hmset(VOLUME_PREFIX + volume_name,
                            {VOLUME_STATUS: VOLUME_STATUS_STARTED, VOLUME_USAGE: -1, VOLUME_CAPACITY: -1,
                            VOLUME_NFS: 'on', VOLUME_SAMBA: 'off', VOLUME_ISCSI: 'off', VOLUME_SWIFT: 'off'})
    else:

        logging.warning('Volume status command:' + result)
    
    service_restart, out = execute_gluster(GLUSTERD_RESTART)
    
    if service_restart:
        return
    else:
        logging.warning('Glusterd restart faild:' + out)

# Volume Commands
# def refresh_volume_status(volume_name='all'):
#     success, result = execute_volume_status(volume_name)
#     # print result
#     if success:
#         for volume in result:
#             volume_name = volume['Status of volume'].strip()
#
#             bricks = list()
#             total_used = 0
#
#             # set volume's brick list
#             for brick in volume['bricks']:
#                 brick_name = brick['Brick']
#                 l_index = brick_name.find(' ')
#                 address = brick_name[l_index:].strip()
#                 free = float(brick['Disk Space Free'][:-2])
#                 total = float(brick['Total Disk Space'][:-2])
#                 total_used += total - free
#                 usage = num2percent((1 - free / total))
#                 brick = {"address": address, "online": 'Y', "usage": usage}
#                 bricks.append(brick)
#             Redis.set(BRICK_PREFIX + volume_name, json.dumps(bricks))
#
#             # add volume name to name-set
#             Redis.sadd(VOLUME_NAMES, volume_name)
#
#             # set volume info for volume created manually
#             volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)
#             if empty(volume_info) or VOLUME_NFS not in volume_info:
#                 Redis.hmset(VOLUME_PREFIX + volume_name,
#                             {VOLUME_STATUS: VOLUME_STATUS_STARTED, VOLUME_USAGE: -1, VOLUME_CAPACITY: -1,
#                              VOLUME_NFS: 'on', VOLUME_SAMBA: 'off', VOLUME_ISCSI: 'off', VOLUME_SWIFT: 'off'})
#     else:
#         logging.warning('Volume status command:' + result)


# Volume Commands
def refresh_volume_status(volume_name='all'):
    Redis.psetex("volumeOperate", 1000, "ll")
    success, result, volume_stop = execute_volume_status(volume_name)
    # print result
    if success:
        volume_running = list()
        if len(result):
            for volume in result:
                volume_name = volume['Status of volume'].strip()
                # volume_name is volume's name who is running
                if volume_name is None:
                    logging.warning('volume_name is None:' + volume_name + ':' + str(sys._getframe().f_lineno) )
                volume_running.append(volume_name)
                bricks = list()
                total_used = 0

                # set volume's brick list
                for brick in volume['bricks']:
                    # print brick
                    brick_name = brick['Brick']
                    l_index = brick_name.find(' ')
                    address = brick_name[l_index:].strip()
                    free = float(brick['Disk Space Free'][:-2])
                    total = float(brick['Total Disk Space'][:-2])
                    total_used += total - free
                    usage = num2percent((1 - free / total))
                    brick_state = brick['Online']
                    brick = {"address": address, "online": brick_state, "usage": usage}
                    bricks.append(brick)
                Redis.set(BRICK_PREFIX + volume_name, json.dumps(bricks))
                # add volume name to name-set
                Redis.sadd(VOLUME_NAMES, volume_name)
                # set volume info for volume created manually
                    
                refresh_volume_usage(volume_name)
                
                volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)

                if empty(volume_info) or VOLUME_NFS not in volume_info:
                    Redis.hmset(VOLUME_PREFIX + volume_name,
                            {VOLUME_STATUS: VOLUME_STATUS_STARTED, VOLUME_USAGE: 0, VOLUME_CAPACITY: 0,
                             VOLUME_NFS: 'on', VOLUME_SAMBA: 'off', VOLUME_ISCSI: 'off', VOLUME_SWIFT: 'off'})
                else:
                    Redis.hmset(VOLUME_PREFIX + volume_name,
                                {VOLUME_STATUS: VOLUME_STATUS_STARTED, VOLUME_USAGE: volume_info["usage"],
                                 VOLUME_CAPACITY: volume_info["capacity"], VOLUME_NFS: volume_info["nfs"],
                                 VOLUME_SAMBA: volume_info["samba"], VOLUME_ISCSI: volume_info["iscsi"],
                                 VOLUME_SWIFT: volume_info["swift"]})
        if len(volume_stop):
            for volume in volume_stop:
                volume_info1 = Redis.hgetall(VOLUME_PREFIX + volume)
                if empty(volume_info1) or VOLUME_NFS not in volume_info1:
                    Redis.hmset(VOLUME_PREFIX + volume,
                            {VOLUME_STATUS: VOLUME_STATUS_STOPPED, VOLUME_USAGE: -1, VOLUME_CAPACITY: -1,
                             VOLUME_NFS: 'on', VOLUME_SAMBA: 'off', VOLUME_ISCSI: 'off', VOLUME_SWIFT: 'off'})
                else:
                    Redis.hmset(VOLUME_PREFIX + volume,
                                {VOLUME_STATUS: VOLUME_STATUS_STOPPED, VOLUME_USAGE: volume_info1["usage"],
                                 VOLUME_CAPACITY: volume_info1["capacity"], VOLUME_NFS: volume_info1["nfs"],
                                 VOLUME_SAMBA: volume_info1["samba"], VOLUME_ISCSI: volume_info1["iscsi"],
                                 VOLUME_SWIFT: volume_info1["swift"]})

        volumeAll = list(Redis.sget(VOLUME_NAMES))
        volume_disappear = list((set(volumeAll) | set(volume_running)) - (set(volumeAll) & set(volume_running)))
        volume_deleted = list((set(volume_disappear) | set(volume_stop)) - (set(volume_disappear) & set(volume_stop)))
        if len(volume_deleted):
            for volume_delete_name in volume_deleted:
                #Redis.srem(VOLUME_NAMES, volume_delete_name)
                pass
        Redis.psetex("volumeOperate", 1, "ll")

    else:
        logging.warning('Volume status command:' + result)
    
    service_restart, out = execute_gluster(GLUSTERD_RESTART)
    
    if service_restart:
        return
    else:
        logging.warning('Glusterd restart faild:' + out)


def volume_nfs(volume_name, enable=True):
    if enable:
        return volume_set(volume_name, 'nfs.disable', 'on')
    else:
        return volume_set(volume_name, 'nfs.disable', 'off')


def volume_samba(volume_name, enable=True):
    if enable:
        if samba_search(volume_name):
            return
        execute_samba_on(volume_name)
    else:
        execute_samba_off(volume_name)


def volume_set(volume_name, key, value):
    return execute_gluster(VOLUME_SET + volume_name + ' ' + key + ' ' + value)


'''
    Volume Create Strategy:
    disperse 32+8/32+16:
                  Total brick count is 40/48.
                  Choose 5/6 nodes using Round Robin.
                  Then choose 8 bricks per node.
                  Create new directory identified by volume name in each brick.
'''


def volume_create(nodes, max_dict_idx, volume_name, capacity, redundancy_ratio):
    # return create_rr_tmp(nodes, max_dict_idx, volume_name, capacity, redundancy_ratio)
    return create_round_robin(nodes, max_dict_idx, volume_name, capacity, redundancy_ratio)


# select two nodes from three nodes using RR
def create_round_robin(nodes, max_dict_idx, volume_name, capacity, redundancy_ratio):
    logging.warning('in volume create')
    global cur_node_index

    logging.warning(redundancy_ratio)
    # 32+8
    if redundancy_ratio == 25 or redundancy_ratio == '25':
        total_brick = 40
        disperse = DISPERSE_40
    # 32+16
    elif redundancy_ratio == 50 or redundancy_ratio == '50':
        total_brick = 192
        disperse = DISPERSE_48
    else:
        return False, 'Incorrect redundancy ratio.', -1

    # Change capacity so that it cat be divided exactly by total brick num
    capacity = int(capacity) * 1024
    if capacity % total_brick is not 0:
        capacity = int(capacity / total_brick + 1) * total_brick
    # Use RR to select nodes and bricks
    node_num = total_brick / BRICK_PER_NODE
    dht_num = DHT_NUM
    bricks = ''
    for j in range (dht_num):
        for i in range(node_num):
            node_index = (i + cur_node_index) % len(nodes)
            node = nodes[node_index]
            bricks += generate_bricks_per_node(node, volume_name, max_dict_idx[node], dht_num)
            cur_node_index = (node_num + cur_node_index) % len(nodes)
    # print bricks
    #print VOLUME_CREATE + volume_name + disperse + bricks + FORCE
    # print type(VOLUME_CREATE + volume_name + disperse + bricks + FORCE)
    logging.warning(bricks)

    success, out = execute_gluster(VOLUME_CREATE + volume_name + disperse + TRANSPORT_TYPE +bricks + FORCE)
    return success, out, capacity


# select two nodes from three nodes using RR
def create_rr_tmp(nodes, max_dict_idx, volume_name, capacity, redundancy_ratio):
    global cur_node_index

    if redundancy_ratio == 25 or redundancy_ratio == '25':
        total_brick = 4
        disperse = DISPERSE__3_1
    elif redundancy_ratio == 33 or redundancy_ratio == '33':
        total_brick = 6
        disperse = DISPERSE__4_2
    else:
        return False, 'Incorrect redundancy ratio.'

    # Change capacity so that it cat be divided exactly by total brick num
    capacity = int(capacity) * 1024
    if capacity % total_brick is not 0:
        capacity = int(capacity / total_brick + 1) * total_brick

    # Use RR to select nodes and bricks
    node_num = total_brick / BRICK_PER_NODE
    dht_num = DHT_NUM
    bricks = ''
    for j in range (dht_num):
        for i in range(node_num):
            node_index = (i + cur_node_index) % len(nodes)
            node = nodes[node_index]
            bricks += generate_bricks_per_node(node, volume_name, max_dict_idx[node], dht_num)
            cur_node_index = (node_num + cur_node_index) % len(nodes)
    # print bricks+
    #print VOLUME_CREATE + volume_name + disperse + bricks + FORCE
    # print type(VOLUME_CREATE + volume_name + disperse + bricks + FORCE)

    success, out = execute_gluster(VOLUME_CREATE + volume_name + disperse + TRANSPORT_TYPE +bricks + FORCE)
    return success, out, capacity

#def generate_bricks_all(nodes, node_num, vol_name, brick_num, dht_num):

#    bricks = ''
    
#    for i in range(dht_num - 1):
#    for nodeid in range(node_num):
#        node_index = nodeid % len(nodes)
#        node = nodes[node_index]
#        bricks += 


def generate_bricks_per_node(hostname, volume_name, brick_num,  dht_num):
    global cur_brick_record

    node_bricks = ''
    if hostname not in cur_brick_record.keys():
         cur_brick_record[hostname] = 0
    cur_brick_index = cur_brick_record[hostname]
    for i in range(BRICK_PER_NODE / dht_num):
        # plus one:we assume brick index start from one
        brick_index = (i + cur_brick_index) % brick_num
        node_bricks = node_bricks + hostname + ':' + CONFIG_DISK_PREFIX + str(brick_index) + '/' + volume_name + ' '
    
    #cur_brick_index = (BRICK_PER_NODE + cur_brick_index) % brick_num    
    cur_brick_record[hostname] = (BRICK_PER_NODE / dht_num + cur_brick_index) % brick_num
    return str(node_bricks)


def volume_delete(volume_name):
    success, out = execute_confirm(VOLUME_DELETE + volume_name)
    return success, out


def volume_start(volume_name):
    success, result = execute_gluster(VOLUME_START + volume_name)
    # If start successfully,change volume status in redis immediately.
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_STATUS, VOLUME_STATUS_STARTED)
    return success, result


def volume_stop(volume_name):
    cmd = VOLUME_STOP + volume_name + FORCE
    success, result = execute_confirm(cmd)
    # If stop successfully,change volume status in redis immediately.
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_STATUS, VOLUME_STATUS_STOPPED)
    return success, result


# Snapshot Commands

# cmd fail situation: "snapshot create: failed: Snapshot snap2 already exists"
# cmd fail situation: "snapshot create: failed: Volume (vol2) does not exist"
def snapshot_create(volume_name, snapshot_name):
    success, result = execute_gluster(SNAPSHOT_CREATE + snapshot_name + ' ' + volume_name + ' no-timestamp')
    logging.warning(SNAPSHOT_CREATE + snapshot_name + ' ' + volume_name + ' no-timestamp')
    tmp = SNAPSHOT_CREATE + snapshot_name + ' ' + volume_name + ' no-timestamp'
    logging.warning(type(tmp))
    refresh_snapshots()
    return success, result


# cmd fail situation: "snapshot delete: failed: Snapshot (snap4) does not exist"
def snapshot_delete(snapshot_name):
    success, out = execute_confirm(SNAPSHOT_DELETE + snapshot_name)
    refresh_snapshots()
    return success, out


def snapshot_resotre(snapshot_name):
    success, out = execute_confirm(SNAPSHOT_RESOTRE + snapshot_name)
    refresh_snapshots()
    return success, out


# cmd fail situation: "Snapshot info : failed: Volume (volume2) does not exist"
def snapshot_info(volume_name):
    success, out = execute_gluster(SNAPSHOT_INFO + volume_name)
    if success:
        return True, generate_dic_with_subdict(out, 'snapshots', 1, 3, 5)
    else:
        return False, out


def refresh_snapshots():
    volume_names = list(Redis.sget(VOLUME_NAMES))
    for volume_name in volume_names:
        success, out = snapshot_info(volume_name)
        if success:
            if out is not None:
                Redis.set(SNAPSHOT_PREFIX + volume_name, json.dumps(out['snapshots']))
            else:
                Redis.delete(SNAPSHOT_PREFIX + volume_name)
            

# Peer Commands
def peer_probe(hostname):
    success, result = execute_gluster(PEER_PROBE + hostname)
    return success, result


def peer_detach(hostname):
    success, result = execute_gluster(PEER_DETACH + hostname + FORCE)
    return success, result


def peer_status():
    success, out = execute_gluster(PEER_STATUS)
    if success:
        return True, generate_dic_with_subdict(out, 'peers', 0, 1, 4)
    else:
        return False, out

def refresh_pool_list():
    success, result = execute_pool_list()
    if success:
        Redis.set(CLUSTER_LIST, json.dumps(result))
    return result


def enable_volume_quota(volume_name):
    return execute_gluster(VOLUME_QUOTA + volume_name + ENABLE)


def set_volume_quota(volume_name, capacity):
    logging.warning('set quota')
    logging.warning(capacity)
    return execute_gluster(VOLUME_QUOTA + volume_name + VOLUME_QUOTA_LIMIT_USAGE + str(capacity) + GB)


def refresh_volume_usage(volume_name):
    success, out = execute_gluster(VOLUME_QUOTA + volume_name + VOLUME_QUOTA_LIST)
    try:
        if success:
            out = out.split('\n')
            used_capacity = re.split(' +', out[2])[3]
            if used_capacity is None:
                logging.warning('used_capacity is None:' + str(sys._getframe().f_lineno))
                return
            used_num = float(re.match('\d+', used_capacity).group())
            
            available = re.split(' +', out[2])[4]
            avail_num = float(re.match('\d+', available).group())
            if 'GB' in available:
                avail_num = avail_num
            elif 'TB' in available:
                avail_num = avail_num * 1024

            # refresh usage
            str_total_capacity = Redis.hget(VOLUME_PREFIX + volume_name, VOLUME_CAPACITY)
            if str_total_capacity is None:
                logging.warning('str_total_capacity:' + str(sys._getframe().f_lineno))
                return 
            total_capacity = int(Redis.hget(VOLUME_PREFIX + volume_name, VOLUME_CAPACITY))
            if total_capacity==0:
                if 'GB' in available:
                    total_capacity = used_num + avail_num
                elif 'TB' in available:
                    total_capacity = used_num * 1024 + avail_num * 1024
                
            if 'GB' in used_capacity:
                Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_USAGE, num2percent(used_num / total_capacity))
            elif 'TB' in used_capacity:
                Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_USAGE, num2percent(used_num * 1024 / total_capacity))
            else:
                logging.warning(out)
    except (ValueError, IndexError), e:
        logging.warning(e)


def volume_perf(volume_name, read=True):
    if read:
        success, out = execute_gluster(VOLUME_TOP + volume_name + READ_PERF)
    else:
        success, out = execute_gluster(VOLUME_TOP + volume_name + WRITE_PERF)
    perf = 0
    if success:

        out = out.split('\n')
        for line in out:
            line = line.strip().split(' ')
            if len(line) > 0 and line[0].isdigit():
                perf += int(line[0])
    return success, perf


def get_cluster_list():
    cluster_list = json.loads(Redis.get(CLUSTER_LIST))
    machines = list()
    if len(cluster_list) == 0:
        logging.warning("query_machine_resource: Can't get cluster list.")
        return False, machines
    else:
        for machine in cluster_list:
            if machine['status'] == 'Connected':
                machines.append(machine['hostname'])
        return True, machines


def disk_io(hostname):
    disk_info = snmp_query('diskIODevice', hostname, 'public')
    len_disk_info = len(disk_info)
    diskio_write_sds = list()
    diskio_read_sds = list()
    if len_disk_info < 1:
        return "0","0"
    disk_sds = list()
    disk_sds_indexs = list()

    for diskioDevi in disk_info:
        #print diskioDevi
        if "sd" in diskioDevi:
            if 'sdm' in diskioDevi:
               continue
            disk_sds.append(diskioDevi)
            disk_sds_indexs.append(disk_info.index(diskioDevi))
    diskio_writes = snmp_query('diskIONWrittenX', hostname, 'public')
    diskio_reads = snmp_query('diskIONReadX', hostname, 'public')

    Redis.set(CLUSTER_DEVICE+hostname, json.dumps(disk_sds))
    for disk_sds_index in disk_sds_indexs:
        diskio_write_sds.append(diskio_writes[disk_sds_index])
        diskio_read_sds.append(diskio_reads[disk_sds_index])
    # print diskio_read_sds
    return diskio_write_sds, diskio_read_sds

def refresh_disk_io():
    success, cluster_list = get_cluster_list()
    if not success:
        logging.warning("Can't get cluster list.")
        return
    sum_diskio_writes = list()
    sum_diskio_reads = list()
    old_time = Redis.get(TIMESTAMP)
    timestamp = time.time()
    timeStamp = timestamp*1000
    Redis.set(TIMESTAMP, timestamp)
    timeperiod = float(timestamp) - float(old_time)
    for machine in cluster_list:
        diskio_pre = Redis.get(DISKWRITE+machine)
        diskio_read_pre = Redis.get(DISKREAD+machine)
        disk_infmat, diskio_read_infmat = disk_io(machine)
        if none(disk_infmat, diskio_read_infmat):
            return
        Redis.set(DISKWRITE+machine, disk_infmat)
        Redis.set(DISKREAD+machine, diskio_read_infmat)

        # diskwrite str--list
        diskio_pre_list = diskio_pre.replace("[", "").replace("]", "").replace("'", "").strip().split(",")

        # diskread str--list
        diskio_read_pre_list = diskio_read_pre.replace("[", "").replace("]", "").replace("'", "").strip().split(",")
        # disk_write lambda
        diskio_pre_list_num = [int(item) for item in diskio_pre_list]
        disk_infmat_num = [int(item) for item in disk_infmat]
        write_D_value = list(map(lambda x: abs(x[0] - x[1]), zip(disk_infmat_num, diskio_pre_list_num)))
        sum_diskio_writes.append(write_D_value)
        sum_name_write = 0
        for x in write_D_value:
            if x <= 0:
                x = 0
            sum_name_write += x
        sum_name_write_throughtput = sum_name_write / timeperiod
        Redis.lpush(DISK_NAME_WRITE + machine, {DATA: sum_name_write_throughtput, TIME: timeStamp})

        # disk_read lamba
        diskio_read_pre_list_num = [int(item) for item in diskio_read_pre_list]
        diskio_read_infmat_num = [int(item) for item in diskio_read_infmat]
    
        read_D_value = list(map(lambda x: abs(x[0] - x[1]), zip(diskio_read_infmat_num, diskio_read_pre_list_num)))
        sum_diskio_reads.append(read_D_value)
        sum_name_read = 0
        for x in read_D_value:
            if x <= 0:
                x = 0
            sum_name_read += x
        sum_name_read_throughput = sum_name_read / timeperiod
        Redis.lpush(DISK_NAME_READ + machine, {DATA: sum_name_read_throughput, TIME: timeStamp})
    i = 0
    sum_writes = 0
    sum_reads = 0
    sum_diskio_write = list()
    sum_diskio_read = list()

    while i < len(sum_diskio_writes):
        sum_write = 0
        sum_read = 0
        for x in sum_diskio_writes[i]:
            sum_write += x
        sum_diskio_write.append(sum_write/(timeperiod))
    
        for y in sum_diskio_reads[i]:
            sum_read += y
        sum_diskio_read.append(sum_read/(timeperiod))
        i += 1
    for x in sum_diskio_write:
        sum_writes += x
    for y in sum_diskio_read:
        sum_reads += y

    Redis.lpush(DISKWRITEALL, {DATA: sum_writes, TIME: timeStamp})
    Redis.lpush(DISKREADALL, {DATA: sum_reads, TIME: timeStamp})


def network_io(hostname):
    networkIO = snmp_query('ifName', hostname, 'public')
    #print networkIO
    len_networkIO = len(networkIO)
    if len_networkIO < 1:
        return "0","0"
    network_io_in_all = snmp_query('ifHCInOctets', hostname, 'public')
    network_io_out_all = snmp_query('ifHCOutOctets', hostname, 'public')
    ib0_index = networkIO.index("ib0")
    #print ib0_index
    networkIO_in = network_io_in_all[ib0_index]
    networkIO_out = network_io_out_all[ib0_index]
    return networkIO_in, networkIO_out

def refresh_network_io():
    success, cluster_list = get_cluster_list()
    if not success:
        return
    list_network_in_speed = list()
    list_network_out_speed = list()
    old_time = Redis.get(TIMESTAMP + "network")
    timestamp = time.time()
    timeStamp = timestamp * 1000
    Redis.set(TIMESTAMP+"network", timestamp)
    timeperiod = float(timestamp) - float(old_time)
    for machine in cluster_list:
        network_in_pre = Redis.get(NETWORKIO_IN+machine)
        network_out_pre = Redis.get(NETWORKIO_OUT+machine)
        # print network_in_pre
        network_io_in, network_io_out = network_io(machine)
        if none(network_io_in, network_io_out):
            return
        Redis.set(NETWORKIO_IN+machine, network_io_in)
        Redis.set(NETWORKIO_OUT+machine, network_io_out)
        network_io_in_speed = int(network_io_in) - int(network_in_pre)
        network_io_out_speed = int(network_io_out) - int(network_out_pre)
        if network_io_out_speed <= 0:
            network_io_out_speed = 0
        if network_io_in_speed <= 0:
            network_io_in_speed = 0
        network_io_in_speed_throughput = network_io_in_speed / timeperiod
        network_io_out_speed_throughput = network_io_out_speed / timeperiod
        list_network_in_speed.append(network_io_in_speed_throughput)
        list_network_out_speed.append(network_io_out_speed_throughput)
        Redis.lpush(NETWORKIO_NAME_IN_INIT + machine, {DATA: network_io_in_speed_throughput, TIME: timeStamp})
        Redis.lpush(NETWORKIO_NAME_OUT_INIT + machine, {DATA: network_io_out_speed_throughput, TIME: timeStamp})

    sum_network_in_speed = 0
    sum_network_out_speed = 0
    for x in list_network_in_speed:
        sum_network_in_speed += x
    for y in list_network_out_speed:
        sum_network_out_speed += y
    Redis.lpush(NETWORKIO_IN_SUM_INIT, {DATA: sum_network_in_speed, TIME: timeStamp})
    Redis.lpush(NETWORKIO_OUT_SUM_INIT, {DATA: sum_network_out_speed, TIME: timeStamp})


def monitor_resource(hostname):
    storage_size = snmp_query('hrStorageSize', hostname, 'public')
    #print "hahaha"
    # print len(storage_size)
    storage_used = snmp_query('hrStorageUsed', hostname, 'public')
    storage_descr = snmp_query('hrStorageDescr', hostname, 'public')
    # To do:raise err if snmp can't get machine info.
    len_storage_descr = len(storage_descr)
    len_storage_used = len(storage_used)
    len_storage_size = len(storage_size)

    #print "hahaha2"
    # print storage_descr
    # print len_storage_descr
    resource = dict()
    memory = dict()
    memory_usage = 0
    pure_disks = list()
    total_size = 0
    used_size = 0
    cpu_usages = list()
    
    if len_storage_descr < 1 or len_storage_used < 1 or len_storage_size < 1 or len_storage_descr != len_storage_used or len_storage_descr != len_storage_size :
        # print "bug here"
        return resource, memory_usage, cpu_usages, pure_disks, total_size, used_size
    
    #print "before"
    # print len(storage_size)
    # print len(storage_used)
    if storage_descr[0] == 'Physical memory':
        memory['size'] = kb2gb(float(storage_size[0]))
        memory_usage = num2percent(float(storage_used[0]) / float(storage_size[0]))

    # disks
    i = 5
    disks = list()
    # collect this message for query_cluster_disks()
    total_size = 0
    used_size = 0
    # print "here"
    while i < len_storage_descr:
        # /brick/brickX is appointed disk mount directory
        if CONFIG_DISK_PREFIX in storage_descr[i]:
            disk = dict()
            disk['name'] = storage_descr[i]
            pure_disks.append(storage_descr[i])
            disk_total = int(storage_size[i]) / 250000
            disk_used = int(storage_used[i]) / 250000
            

        #print hostname+":"+ storage_used[i]
            disk['size'] = disk_total
            total_size += disk_total
            used_size += disk_used
            disk['usage'] = num2percent(float(storage_used[i]) / float(storage_size[i]))
            disks.append(disk)
        i += 1

    # cpus
    processor_load = snmp_query('hrProcessorLoad', hostname, 'public')
    device_descr = snmp_query('hrDeviceDescr', hostname, 'public')
    cpus = list()

    i = 0
    # print processor_load
    while i < len(processor_load):
        cpu = dict()
        cpu['name'] = device_descr[i]
        cpu_usages.append(processor_load[i])
        cpus.append(cpu)
        i += 1

    
    resource['hostname'] = hostname
    resource['memory'] = memory
    resource['disks'] = disks
    resource['cpus'] = cpus
    # print pure_disks
    return resource, memory_usage, cpu_usages, pure_disks, total_size, used_size

def refresh_machine_resource():
    Redis.psetex("volumeOperate", 1000, "ll")
    success, cluster_list = get_cluster_list()
    # print cluster_list
    resource_list = list()
    disks_dict = dict()
    if not success:
        logging.warning("Can't get cluster list.")
        return
    total = 0
    used = 0
    for machine in cluster_list:
        if machine is None:
            logging.warning('machine:' + machine + ':' + str(sys._getframe().f_lineno))
            continue
        resource, memory_usage, cpu_usages, pure_disks, total_size, used_size = monitor_resource(machine)
        total += total_size
        used += used_size
        # print resource
        # Log error when any machine's snmp service shut down.
        #if none(resource, memory_usage, cpu_usages, pure_disks):
        if len(resource)==0:
            logging.error('Please start snmp service in machine: ' + machine + '.' + str(sys._getframe().f_lineno))
            continue
        resource_list.append(resource)
        disks_dict[machine] = pure_disks
        Redis.lpush(MEMORY_USAGE_PREFIX + machine, memory_usage)
        i = 0
        while i < len(resource['cpus']):
            Redis.lpush(CPU_USAGE_PREFIX + machine + ':' + str(i), cpu_usages[i])
            i += 1
    Redis.hmset(OVERALL_CAPACITY, {'total': total, 'used': used, 'available': (total - used)})
    Redis.set(CLUSTER_RESOURCE, json.dumps(resource_list))
    Redis.set(CLUSTER_DISKS, json.dumps(disks_dict))
    Redis.psetex("volumeOperate", 1, "ll")


'''
def query_machine_resource_local():
    resource_dict = dict()
    resource_dict[CONFIG_LOCAL_HOST], memory_usage, cpu_usages = monitor_resource(CONFIG_LOCAL_HOST)
    Redis.lpush(MEMORY_USAGE_PREFIX + CONFIG_LOCAL_HOST, memory_usage)
    i = 0
    while i < len(resource_dict[CONFIG_LOCAL_HOST]['cpus']):
        Redis.lpush(CPU_USAGE_PREFIX + CONFIG_LOCAL_HOST + ':' + str(i), cpu_usages[i])
        i += 1
    Redis.set(CLUSTER_RESOURCE, json.dumps(resource_dict))
'''


def query_volume_perf():
    volume_names = list(Redis.sget(VOLUME_NAMES))
    for volume_name in volume_names:
        success, read_perf = volume_perf(volume_name)
        if success:
            Redis.lpush(READ_SPEED_PREFIX + volume_name, read_perf)
        success, write_perf = volume_perf(volume_name, False)
        if success:
            Redis.lpush(WRITE_SPEED_PREFIX + volume_name, write_perf)


# thread function
def query_periodically():
    while True:
        try:
            logging.warning('in query')
            # refresh_pool_list()
            # refresh_machine_resource()
            # query_volume_perf()
            refresh_volume_status()
            sleep(CONFIG_QUERY_PERIOD)
        except Exception, e:
            logging.warning(e)

#
# def refresh_volume_data(volume_name="all"):
#
#
#     success, result = execute_volume_status(volume_name)
#     if success:
#         volume_list= list();
#         for volume in result:
#             volume_name = volume['Status of volume'].strip()
#
#             volume_list.append(volume_name)
#         print volume_list
#         volume_list_in_redis = Redis.sget(VOLUME_NAMES)
#
#         for volume_in_redis in volume_list_in_redis:
#             if volume_in_redis in volume_list:
#                 continue
#             else:
#                 Redis.srem(volume_in_redis, VOLUME_NAMES)
#                 Redis.delete(BRICK_PREFIX + volume_in_redis)
#                 Redis.delete(VOLUME_PREFIX + volume_in_redis)
#     else:
#         logging.warning("refresh_volume_data FAILED" + result);


'''

def monitor_resource_test(hostname):
    storage_size = snmp_query('hrStorageSize', hostname, 'public')
    storage_used = snmp_query('hrStorageUsed', hostname, 'public')
    storage_descr = snmp_query('hrStorageDescr', hostname, 'public')

    len_storage_descr = len(storage_descr)
    if len_storage_descr < 1:
        return

    # disks
    i = 5
    disks = list()
    # collect this message for query_cluster_disks()
    while i < len_storage_descr:
        logging.warning(storage_descr[i])
        # /brick/brickX is appointed disk mount directory
        if CONFIG_DISK_PREFIX in storage_descr[i]:
            disk = dict()
            disk['name'] = storage_descr[i]
            disk['size'] = int(storage_size[i]) / 250000
            disk['usage'] = num2percent(float(storage_used[i]) / float(storage_size[i]))
            disks.append(disk)
        i += 1
    logging.warning(disks)
'''

'''


# Used in tfs
# transport:default rdma
def create_rr(volume_name, capacity, redundancy_ratio):
    global cur_node_index
    # 32+8
    if redundancy_ratio == 25:
        total_brick = 40
        disperse = DISPERSE_40
    # 32+16
    elif redundancy_ratio == 50:
        total_brick = 48
        disperse = DISPERSE_48
    else:
        return False, 'Incorrect redundancy ratio.'
    # TB to GB
    capacity = int(capacity) * 1024
    if capacity % total_brick is not 0:
        capacity = int(capacity / total_brick + 1) * total_brick
    success, cluster_list = get_cluster_list()
    if not success:
        return False, "Can't get cluster list."
    node_num = total_brick / BRICK_PER_NODE
    bricks = ''
    for i in range(node_num):
        # Round Robin
        node_index = (i + cur_node_index) % len(cluster_list)
        bricks += generate_bricks_per_node(cluster_list[node_index], volume_name)
    cur_node_index = (node_num + cur_node_index) % len(cluster_list)
    # return VOLUME_CREATE + volume_name + disperse + bricks + FORCE

    # volume capacity = quota
    # volume usage = 0
    success, result = execute_gluster(VOLUME_CREATE + volume_name + disperse + bricks + FORCE)


# unused Brick Commands:Not supported by disperse volume

def volume_addbrick(volume_name, new_brick):
    # cmd = [GLUSTER, VOLUME, 'add-brick', volume_name, new_brick]
    success, result = execute_gluster('gluster volume add-brick ' + volume_name + ' ' + new_brick + ' force')
    return success, result


def volume_removebrick(volume_name, brick, force=True):
    cmd = [GLUSTER, VOLUME, 'remove-brick', volume_name, brick]
    if force:
        cmd += ['force']
    execute_confirm(cmd)


def volume_replacebrick(volume_name, brick, new_brick):
    # cmd = [GLUSTER, VOLUME, 'replace-brick', volume_name, brick, new_brick, 'commit', 'force']
    success, result = execute_gluster(
        'gluster volume replace-brick ' + volume_name + ' ' + brick + ' ' + new_brick + ' commit force')
    return success, result


# We use snmp instead of lsblk now.

def query_cluster_disks():
    machines = pool_list()
    disk_dict = dict()
    for machine in machines:
        disk_dict[machine['hostname']] = get_machine_disks(machine['hostname'])
    Redis.set(CLUSTER_DISKS, json.dumps(disk_dict))


def get_machine_disks(hostname):
    if hostname == LOCAL_HOST:
        success, disk_info = execute_gluster(LSBLK)
    else:
        success, disk_info = execute_ssh(hostname, LSBLK)
    disks = list()
    if not success:
        return disks
    else:
        disk_info = disk_info.split("\n")
        for line_data in disk_info:
            if re.search('disk', line_data, re.IGNORECASE):
                line_data_token = re.split(' +', line_data)
                if line_data_token[-1]:
                    disks.append(line_data_token[-1])
        return disks


# unused volume info:We modify volume status when stopping/starting volume

def volume_info():
    success, datas = execute_volume_info()
    if success:
        for volume in datas:
            Redis.hset(VOLUME_PREFIX + volume['Volume Name'], VOLUME_STATUS, volume['Status'])
    else:
        logging.warning('Volume info command:' + datas)


'''
