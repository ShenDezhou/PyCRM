from flask import Flask, request, jsonify, render_template

from flask_cache import Cache
from redis_util import *
from command import snapshot_create, snapshot_delete, volume_delete, volume_start, volume_stop, volume_create, \
    volume_nfs, get_cluster_list, refresh_createvolume_status, enable_volume_quota, set_volume_quota, volume_samba
import simplejson as json
from config import CONFIG_MONITOR_LIST_LEN, CONFIG_PERF_LIST_LEN, CONFIG_REDUNDANCY_RATIO, CONFIG_LOCAL_IP
from check_util import none, empty
import logging
import random
#gevent
# gevent
from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()
# gevent end


app = Flask(__name__)

INVALID_PARAM = 'Invalid parameters.'
NO_INFORMATION = 'No information at present.'
DIS_MATCH_INFORMATION = 'Information dismatch.'
START_SNMP_SERVICE = 'Please start snmp service on cluster.'

cache = Cache(app,config={'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST':'localhost',
    'CACHE_REDIS_PORT':6379,
    'CACHE_REDIS_PASSWORD':'',
    'CACHE_REDIS_DB':0})

@app.route('/')
def init():
    # try:
        # Get the cluster capacity firstly
        # capacity = Redis.hgetall(OVERALL_CAPACITY)
        # if empty(capacity):
        #     return jsonify(success=False, message=START_SNMP_SERVICE)
        # volume_names_set = Redis.sget(VOLUME_NAMES)
        # # There is no volume yet
        # if empty(volume_names_set):
        #     return render_template('/index.html')
        # volume_names = list(volume_names_set)
        # volumes = list()
        # for volume_name in volume_names:
        #     volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)
        #     volume_info['name'] = volume_name
        #     volume_info['usage'] = Redis.hget(VOLUME_PREFIX + volume_name, 'usage')
        #     # frontend just check whether volume info has key 'nfs' 'samba' 'iscsi' 'swift'
        #     # volume_info['nfs'] = 'on'
        #
        #     bricks = Redis.get(BRICK_PREFIX + volume_name)
        #     if bricks is None:
        #         bricks = []
        #     else:
        #         bricks = json.loads(bricks, 'utf-8')
        #     volume_info['bricks'] = bricks
        #
        #     snapshots = Redis.get(SNAPSHOT_PREFIX + volume_name)
        #     if snapshots is None:
        #         snapshots = ''
        #     else:
        #         snapshots = json.loads(snapshots, 'utf-8')
        #     volume_info['snapshots'] = snapshots
        #
        #     read = Redis.lrange(READ_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
        #     write = Redis.lrange(WRITE_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
        #     fill_list(read)
        #     fill_list(write)
        #     volume_info['read'] = read
        #     volume_info['write'] = write
        #     set_client_info(volume_info)
        #     volumes.append(volume_info)
        #
        #     cluster_list = json.loads(Redis.get(CLUSTER_LIST), 'utf-8')
        #     cluster_disks = json.loads(Redis.get(CLUSTER_DISKS), 'utf-8')
        #     servers = list()
        #     for machine in cluster_list:
        #         server = dict()
        #         server['serverId'] = machine['hostname']
        #         server['serverStatus'] = machine['status']
        #         disks = list()
        #         if machine['status'] == 'Disconnected':
        #             continue
        #         raw_disks = cluster_disks[machine['hostname']]
        #         for raw_disk in raw_disks:
        #             disk = dict()
        #             disk['diskId'] = raw_disk
        #             disk['diskStatus'] = 'health'
        #             disks.append(disk)
        #         server['disks'] = disks
        #         servers.append(server)
    # except (TypeError, KeyError), e:
    #     logging.warning("hello:"+ str(e))
    return render_template('/index.html')


# To Do: Add Username and Password
def set_client_info(volume_info):
    client_list = ['nfs', 'samba', 'iscsi', 'swift']
    clientInfo_list = ['nfsInfo', 'sambaInfo', 'iscsiInfo', 'swiftInfo']
    for i in range(len(client_list)):
        client = client_list[i]
        if client in volume_info.keys() and volume_info[client] == 'on':
            volume_info[clientInfo_list[i]] = {'address': CONFIG_LOCAL_IP, 'username': '--', 'password': '--'}
        else:
            volume_info[clientInfo_list[i]] = {'address': '--', 'username': '--', 'password': '--'}


# page 0: system overview
'''

@app.route('/overview/capacity')
def get_overview_capacity():
    try:
        return jsonify( Redis.hgetall(OVERALL_CAPACITY))
    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)


@app.route('/overview/volumes')
def get_overview_volumes():
    try:
        volume_names = list(Redis.sget(VOLUME_NAMES))
        volumes = list()
        for volume_name in volume_names:
            volumes.append(Redis.hgetall(VOLUME_PREFIX + volume_name))
        return jsonify(volume_nums=len(volume_names), volumes=volumes)
    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)


# page 1: volume management
@app.route('/volume/names')
def get_volume_names():
    try:
        volume_names = list(Redis.sget(VOLUME_NAMES))
        return jsonify(names=volume_names)
    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)
'''



'''
@app.route('/volume/<string:volume_name>')
def get_volume_info(volume_name):
    usage = Redis.hget(VOLUME_PREFIX + volume_name, 'usage')
    bricks = Redis.get(BRICK_PREFIX + volume_name)
    snapshots = Redis.get(SNAPSHOT_PREFIX + volume_name)
    return jsonify(usage=usage, bricks=bricks, snapshots=snapshots)
'''


@app.route('/volume/add')
def add_volume():
    try:
        Redis.psetex("Refresh", 25000, "ll")
        time = Redis.get("volumeOperate")
        if time:
            time.sleep(0.5)
        # parse request form
        volume_name = request.args.get('name')
        capacity = request.args.get('capacity')
        redundancy_ratio = request.args.get('redundancy_ratio')
        if none(volume_name, capacity, redundancy_ratio):
            return jsonify(success=False, message='Request form lacks parameters.')

        volume_name = str(volume_name)
        capacity = str(capacity)
        redundancy_ratio = str(redundancy_ratio)
        logging.warning(redundancy_ratio)

        # query nodes and disks,then generate max disk index per node
        cluster_disks = json.loads(Redis.get(CLUSTER_DISKS), 'utf-8')
        success, cluster_list = get_cluster_list()
        max_dict_idx = dict()
        if not success:
            return jsonify(success=False, message=NO_INFORMATION)
        keys = cluster_disks.keys()
        for node in cluster_list:
            if node not in keys:
                return jsonify(success=False, message=DIS_MATCH_INFORMATION)
            else:
                max_dict_idx[node] = len(cluster_disks[node])

        # dict = {"01": "volume_create1", "cluster_list": cluster_list, "max_dict_idx": max_dict_idx,
        #         "volume_name": volume_name, "capacity": capacity, "redundancy_ratio": redundancy_ratio}

        Redis.lpush()

        success, out, actual_capacity = volume_create(cluster_list, max_dict_idx, volume_name, capacity,
                                                      redundancy_ratio)
        if success:
            volume_start(volume_name)
            # related configuration: enable quota and set redis
            enable_volume_quota(volume_name)
            set_volume_quota(volume_name, actual_capacity)
            Redis.hmset(VOLUME_PREFIX + volume_name,
                        {VOLUME_CAPACITY: actual_capacity, VOLUME_USAGE: 0, VOLUME_NFS: 'on', VOLUME_SAMBA: 'off',
                         VOLUME_ISCSI: 'off', VOLUME_SWIFT: 'off'})
            refresh_createvolume_status(volume_name)
            volume_info = get_volume_info(volume_name)
            Redis.psetex("Refresh", 1, "ll")
            return jsonify(success=True, message=volume_info)
        else:
            return jsonify(success=False, message=out)

    except (KeyError, TypeError), e:
        return jsonify(success=False, message=str(e))


def get_volume_info(volume_name):
    volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)
    volume_info['name'] = volume_name
    volume_info['usage'] = 0
    bricks = Redis.get(BRICK_PREFIX + volume_name)
    if bricks is None:
        bricks = []
    else:
        bricks = json.loads(bricks, 'utf-8')
    volume_info['bricks'] = bricks
    volume_info['snapshots'] = []
    read = list()
    write = list()
    fill_list(read)
    fill_list(write)
    volume_info['read'] = read
    volume_info['write'] = write
    volume_info['nfsInfo'] = {'address': CONFIG_LOCAL_IP, 'username': '--', 'password': '--'}
    volume_info['sambaInfo'] = {'address': '--', 'username': '--', 'password': '--'}
    volume_info['iscsiInfo'] = {'address': '--', 'username': '--', 'password': '--'}
    volume_info['swiftInfo'] = {'address': '--', 'username': '--', 'password': '--'}
    return volume_info


@app.route('/volume/remove')
def delete_volume():
    try:
        Redis.psetex("Refresh", 10000, "ll")
        time = Redis.get("volumeOperate")
        if time:
            time.sleep(0.5)
        volume_name = request.args.get('name')
        logging.warning(volume_name)
        if none(volume_name):
            return jsonify(success=False, message=INVALID_PARAM)
        volume_name = str(volume_name)

        # check if volume exists and if volume has already stopped.
        volume_names = list(Redis.sget(VOLUME_NAMES))
        volume_status = Redis.hget(VOLUME_PREFIX + volume_name, VOLUME_STATUS)
        if volume_name not in volume_names or volume_status != VOLUME_STATUS_STOPPED:
            return jsonify(success=False, message=INVALID_PARAM)

        success, out = volume_delete(volume_name)

        # clear volume information in redis
        if success:
            # remove data from redis
            Redis.srem(VOLUME_NAMES, volume_name)
            Redis.delete(BRICK_PREFIX + volume_name)
            Redis.delete(VOLUME_PREFIX + volume_name)

            # remove data from samba config file
            volume_samba(volume_name, enable=False)
            Redis.psetex("Refresh", 1, "ll")
        return jsonify(success=success, message=out)

    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)


'''
@app.route('/volume/<string:volume_name>/speed')
def volume_perf(volume_name):
    try:
        read = Redis.lrange(READ_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
        write = Redis.lrange(WRITE_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
        fill_list(read)
        fill_list(write)
        return jsonify(success=True, read=read, write=write)
    except KeyError:
        return jsonify(success=False, message=NO_INFORMATION)
'''


# perf[read_perf,write_perf]
@app.route('/volume/perf')
def volume_read_perf():
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    perf = [random.randint(1, 10), random.randint(1, 10)]
    return jsonify(success=True, message=perf)


@app.route('/volume/self/start')
def start_volume():
    Redis.psetex("Refresh", 20000, "ll")
    time = Redis.get("volumeOperate")
    if time:
        time.sleep(0.5)
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)
    success, out = volume_start(volume_name)
    Redis.psetex("Refresh", 1, "ll")
    return jsonify(success=success, message=out)


@app.route('/volume/self/stop')
def stop_volume():
    try:
        Redis.psetex("Refresh", 20000, "ll")
        time = Redis.get("volumeOperate")
        if time:
            time.sleep(0.5)
        volume_name = request.args.get('volume_name')
        if none(volume_name):
            return jsonify(success=False, message=INVALID_PARAM)
        volume_name = str(volume_name)
        success, out = volume_stop(str(volume_name))
        Redis.psetex("Refresh", 1, "ll")
        return jsonify(success=success, message=out)
    except Exception, e:
        return jsonify(success=False, message=str(e))


@app.route('/volume/self/restart')
def restart_volume():
    Redis.psetex("Refresh", 20000, "ll")
    time = Redis.get("volumeOperate")
    if time:
        time.sleep(0.5)
    volume_name = request.args.get('volume_name')

    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)
    volume_status = Redis.hget(VOLUME_PREFIX + volume_name, VOLUME_STATUS)
    if none(volume_status) or volume_status == VOLUME_STATUS_STOPPED:
        return jsonify(success=False, message=INVALID_PARAM)

    stop_success, stop_out = volume_stop(volume_name)
    if stop_success:
        start_success, start_out = volume_start(volume_name)
        if start_success:
            Redis.psetex("Refresh", 1, "ll")
            return jsonify(success=True, message=start_out)
        else:
            return jsonify(success=False, message=start_out)
    else:
        return jsonify(success=False, message=stop_out)


@app.route('/volume/nfs/stop/<string:volume_name>')
def stop_nfs_test(volume_name):
    volume_name = str(volume_name)

    success, out = volume_nfs(volume_name, enable=False)
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_NFS, 'off')
    return jsonify(success=success, message=out)


@app.route('/volume/nfs/start/<string:volume_name>')
def start_nfs_test(volume_name):
    volume_name = str(volume_name)

    success, out = volume_nfs(volume_name, enable=True)
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_NFS, 'on')
    return jsonify(success=success, message=out)


# /volume/<volume_name>/nfs/start
# /volume/<volume_name>/nfs/stop
@app.route('/volume/nfs/start')
def start_nfs():
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)

    success, out = volume_nfs(volume_name, enable=True)
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_NFS, 'on')
    return jsonify(success=success, message=out)


@app.route('/volume/nfs/stop')
def stop_nfs():
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)

    success, out = volume_nfs(volume_name, enable=False)
    if success:
        Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_NFS, 'off')
    return jsonify(success=success, message=out)


@app.route('/volume/samba/start')
def start_samba():
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)

    volume_samba(volume_name, enable=True)
    Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_SAMBA, 'on')
    return jsonify(succuss=True, message=None)


@app.route('/volume/samba/stop')
def stop_samba():
    volume_name = request.args.get('volume_name')
    if none(volume_name):
        return jsonify(success=False, message=INVALID_PARAM)
    volume_name = str(volume_name)

    volume_samba(volume_name, enable=False)

    Redis.hset(VOLUME_PREFIX + volume_name, VOLUME_SAMBA, 'off')
    return jsonify(succuss=True, message=None)


# @app.route('/snapshot/add')
# def add_snapshot(volume_name, snapshot_name):
#     volume_name = request.args.get('volume_name')
#     snapshot_name = request.args.get('snapshot_name')
#     if none(volume_name, snapshot_name):
#         return jsonify(success=False, message=INVALID_PARAM)
#     volume_name = str(volume_name)
#     snapshot_name = str(snapshot_name)
#
#     success, out = snapshot_create(volume_name, snapshot_name)
#     return jsonify(success=success, message=out)


# @app.route('/snapshot/remove')
# def delete_snapshot(snapshot_name):
#     snapshot_name = request.args.get('snapshot_name')
#     if none(snapshot_name):
#         return jsonify(success=False, message=INVALID_PARAM)
#     snapshot_name = str(snapshot_name)
#
#     success, out = snapshot_delete(snapshot_name)
#     return jsonify(success=success, message=out)


# @app.route('/snapshot/resotre')
# def restore_snapshot():
#     snapshot_name = request.args.get('snapshot_name')
#     if none(snapshot_name):
#         return jsonify(success=False, message=INVALID_PARAM)
#     snapshot_name = str(snapshot_name)
#
#     success, out = snapshot_restore(snapshot_name)
#     return jsonify(success=success, message=out)


# @app.route('/snapshot/<string:volume_name>')
# def get_snapshot(volume_name):
#     snapshots = Redis.get(SNAPSHOT_PREFIX + volume_name)
#     if snapshots is None:
#         snapshots = []
#         return jsonify(success=False, message=snapshots)
#     else:
#         snapshots = json.loads(snapshots, 'utf-8')
#         return jsonify(success=True, message=snapshots)


# page 2: system management
@app.route('/cluster/info')
@cache.cached(timeout=1)
def get_cluster_info():
    servers = list()
    write_reads = list()
    init_write_reads = list()
    cluster_list = json.loads(Redis.get(CLUSTER_LIST), 'utf-8')
    try:
        for machine in cluster_list:
            server = dict()
            server['serverId'] = machine['hostname']
            server['serverStatus'] = machine['status']
            cluster_devices = json.loads(Redis.get(CLUSTER_DEVICE+machine['hostname']), 'utf-8')
            disks = list()
            if machine['status'] == 'Connected':
                raw_disks = cluster_devices
                for raw_disk in raw_disks:
                    disk = dict()
                    disk['diskId'] = raw_disk
                    disk['diskStatus'] = 'health'
                    disks.append(disk)
            server['disks'] = disks
            servers.append(server)

        i = 0
        while i < len(cluster_list):
            write_read = dict()
            hostname = cluster_list[i]["hostname"]
            hoststatus = cluster_list[i]['status']
            if hoststatus == 'Connected':
                # machine_diskio
                write_read["init_disk_write_data"] = Redis.lrange(DISK_NAME_WRITE + hostname, -360, -1)
                write_read["init_disk_read_data"] = Redis.lrange(DISK_NAME_READ + hostname, -360, -1)
                # machine_networkio
                write_read["init_network_in_data"] = Redis.lrange(NETWORKIO_NAME_IN_INIT + hostname, -360, -1)
                write_read["init_network_out_data"] = Redis.lrange(NETWORKIO_NAME_OUT_INIT + hostname, -360, -1)
                write_reads.append(write_read)
            i += 1
        init_write_read = dict()
        # sum_diskio
        init_write_read["init_disk_write_sum"] = Redis.lrange(DISKWRITEALL, -360, -1)
        init_write_read["init_disk_read_sum"] = Redis.lrange(DISKREADALL, -360, -1)
        # sum_networkio
        init_write_read["init_network_in_sum"] = Redis.lrange(NETWORKIO_IN_SUM_INIT, -360, -1)
        init_write_read["init_network_out_sum"] = Redis.lrange(NETWORKIO_OUT_SUM_INIT, -360, -1)
        init_write_reads.append(init_write_read)
        return jsonify(success=True, servers=servers, write_reads=write_reads, init_write_reads = init_write_reads)
    except (TypeError, KeyError):
        return jsonify(success=False, message=NO_INFORMATION)


# page 3: performance monitor
@app.route('/monitor/info')
@cache.cached(timeout=1)
def get_monitor_info():
    try:
        cluster_resource = Redis.get(CLUSTER_RESOURCE)
        if cluster_resource == 'null':
            return jsonify(success=False)
        cluster_resource = json.loads(cluster_resource, 'utf-8')

        i = 0
        # sum_diskio
        # print Redis.lrange(DISKWRITEALL, -20, -1)
        cluster_resource[i]["init_disk_write_sum"] = Redis.lrange(DISKWRITEALL, -2, -1)

        cluster_resource[i]["init_disk_read_sum"] = Redis.lrange(DISKREADALL, -2, -1)
        # sum_networkio
        cluster_resource[i]["init_network_in_sum"] = Redis.lrange(NETWORKIO_IN_SUM_INIT, -2, -1)
        cluster_resource[i]["init_network_out_sum"] = Redis.lrange(NETWORKIO_OUT_SUM_INIT, -2, -1)
        while i < len(cluster_resource):
            machine = cluster_resource[i]
            hostname = machine['hostname']
            memory_usage = Redis.lrange(MEMORY_USAGE_PREFIX + hostname, -30, -1)
            fill_list(memory_usage)
            cluster_resource[i]['memory']['usage'] = memory_usage
            # machine_diskio
            cluster_resource[i]["init_disk_write_data"] = Redis.lrange(DISK_NAME_WRITE + hostname, -2, -1)
            cluster_resource[i]["init_disk_read_data"] = Redis.lrange(DISK_NAME_READ + hostname, -2, -1)
            # machine_networkio
            cluster_resource[i]["init_network_in_data"] = Redis.lrange(NETWORKIO_NAME_IN_INIT + hostname, -2, -1)
            cluster_resource[i]["init_network_out_data"] = Redis.lrange(NETWORKIO_NAME_OUT_INIT + hostname, -2, -1)
            cpus = machine['cpus']
            j = 0
            while j < len(cpus):
                cpu_usage = Redis.lrange(CPU_USAGE_PREFIX + hostname + ':' + str(j), -30, -1)
                fill_list(cpu_usage)
                cpus[j]['usage'] = cpu_usage
                j += 1
            cluster_resource[i]['cpus'] = cpus
            i += 1
        # print cluster_resource
        return jsonify(cluster=cluster_resource)
    except (TypeError, KeyError):
        return jsonify(success=False, message=NO_INFORMATION)


@app.route('/overview/capacity')
@cache.cached(timeout=1)
def get_overview_capacity():
    try:
        volume_info = list()
        capacity = Redis.hgetall(OVERALL_CAPACITY)
        volume_names_set = Redis.sget(VOLUME_NAMES)
        volume_names = list(volume_names_set)
        total = capacity['total']
        available = capacity['available']
        volume_nums = len(volume_names)
        used = capacity['used']
        redundancy_ratio = request.args.get('redundancy_ratio')
        redundancy_ratio = CONFIG_REDUNDANCY_RATIO
        volume_info.append(total)
        volume_info.append(available)
        volume_info.append(volume_nums)
        volume_info.append(used)
        volume_info.append(redundancy_ratio)
        return json.dumps(volume_info)
    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)


@app.route('/overview/volumeData')
@cache.cached(timeout=1)
def get_volume_data():
    try:
        volume_names_set = Redis.sget(VOLUME_NAMES)
        volume_names = list(volume_names_set)
        volumes = list()
        for volume_name in volume_names:
            volume_info = Redis.hgetall(VOLUME_PREFIX + volume_name)
            volume_info['name'] = volume_name
            volume_info['usage'] = Redis.hget(VOLUME_PREFIX + volume_name, 'usage')
            # frontend just check whether volume info has key 'nfs' 'samba' 'iscsi' 'swift'

            bricks = Redis.get(BRICK_PREFIX + volume_name)
            if bricks is None:
                bricks = []
            else:
                bricks = json.loads(bricks, 'utf-8')
            volume_info['bricks'] = bricks

            snapshots = Redis.get(SNAPSHOT_PREFIX + volume_name)
            if snapshots is None:
                snapshots = ''
            else:
                snapshots = json.loads(snapshots, 'utf-8')
            volume_info['snapshots'] = snapshots

            read = Redis.lrange(READ_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
            write = Redis.lrange(WRITE_SPEED_PREFIX + volume_name, -CONFIG_PERF_LIST_LEN, -1)
            fill_list(read)
            fill_list(write)
            volume_info['read'] = read
            volume_info['write'] = write
            set_client_info(volume_info)
            volumes.append(volume_info)
        volumeData = volumes
        return json.dumps(volumeData)
    except TypeError:
        return jsonify(success=False, message=NO_INFORMATION)


def fill_list(l):
    num = CONFIG_MONITOR_LIST_LEN - len(l)
    if num > 0:
        for i in range(num):
            l.append('0')
