from executor import LocalExecutor, SSHExecutor
from config import CONFIG_LOCAL_HOST

VOLUME_INFO_LEN = 10
VOLUME_INFO_LEN_BEFORE_BRICK = 7
VOLUME_INFO_LEN_AFTER_BRICK = 8
VOLUME_STATUS_BRICK_INFO_LEN = 14

local_executor = LocalExecutor()
remote_executor = dict()

VOLUME_STATUS = 'gluster volume status '
DETAIL = ' detail'
VOLUME_INFO = 'gluster volume info'
POOL_LIST = 'gluster pool list'
PING = 'ping -c 1 -q -w 1 '


# execute the command in which we have to send 'y' to confirm operation.
def execute_confirm(cmd):
    return local_executor.execute_confirm(cmd)


def execute_ssh(remote, cmd):
    if remote not in remote_executor.keys():
        remote_executor[remote] = SSHExecutor(remote)
    return remote_executor[remote].execute(cmd)


def execute_gluster(comamnd):
    success, out = local_executor.execute(comamnd, True)
    # if success and ('fail' in out):
    # return False, out
    return success, out


def generate_dic_with_subdict(string, subdict_name, subdict_num_line, subdict_start_line, subdict_length,
                              split_char='\n'):
    result = dict()
    datas = string.split(split_char)
    i = 0

    while i < len(datas):

        # print 'i: '+str(i)
        if i == subdict_num_line:
            generate_key_value_pair(result, datas[i])
            subdict_list = list()
            subdict_num = int(datas[i].split(': ')[1])
            if subdict_num is 0:
                return None
            i += 1
        elif i == subdict_start_line:
            for j in range(subdict_num):
                subdict = dict()
                for k in range(subdict_length):
                    generate_key_value_pair(subdict, datas[i])
                    i += 1
                subdict_list.append(subdict)
            result[subdict_name] = subdict_list
        else:
            generate_key_value_pair(result, datas[i])
            i += 1
    return result


def generate_key_value_pair(dict, line):
    if ':' in line:
        line = line.split(': ')
        if len(line) > 1 and line[1] != '':
            dict[line[0].strip()] = line[1].strip()
            #debug



def execute_pool_list():
    success, out = local_executor.execute(POOL_LIST, False)
    if success:
        host_list = list()
        find_host = False
        # remove command title:'UUID     Hostname 	State'
        del out[0]
        for host in out:
            host_dict = dict()

            host = host.split('\t')
            host_dict['hostname'] = host[1].rstrip()
            # replace localhost with specific hostname
            #if host_dict['hostname'] == 'tfs06':
            #    continue
            if not find_host and (host_dict['hostname'] == 'localhost'):
                host_dict['hostname'] = CONFIG_LOCAL_HOST
                find_host = True
            host_dict['status'] = host[2].strip()
            if host_dict['status'] == "Connected":
                success, out = local_executor.execute(PING+host_dict['hostname'] , False)
                if len(out) != 5 or out[3].find('1 received') == -1:
                    host_dict['status'] = "Disconnected"
            host_list.append(host_dict)
        return True, host_list
    else:
        return False, out


# def execute_volume_status(volume_name='all'):
#     success, datas = local_executor.execute(VOLUME_STATUS + volume_name + DETAIL, False)
#     if success:
#         volume_list = list()
#         i = 0
#         start = 0
#         while i < len(datas):
#             if datas[i] == ' \n':
#                 if 'Status of volume' in datas[start]:
#                     volume = volume_status_parse_volume(datas, start, i)
#                     volume_list.append(volume)
#                 start = i + 1
#             i += 1
#         return True, volume_list
#     else:
#         return False, datas



def execute_volume_status(volume_name='all'):
    success, datas = local_executor.execute(VOLUME_STATUS + volume_name + DETAIL, False)
    if success:
        # datas = datas.split('\n')
        volume_list = list()
        volume_stop_name = list()
        i = 0
        start = 0
        while i < len(datas):
            if datas[i].endswith('\n'):
                # if datas[i] == ' \n':
                if 'Status of volume' in datas[start]:
                    volume = volume_status_parse_volume(datas, start, i)
                    # print volume
                    volume_list.append(volume)
                elif 'not' in datas[start]:
                    if 'Volume detail does not exist' in datas[start]:
                        break
                    volume_list_stop = datas[start]
                    volume_stop_data = volume_list_stop.split(" ")
                    volume_stop_index = volume_stop_data.index('is')
                    volume_stop_name.append(volume_stop_data[volume_stop_index-1])
                start = i + 1
            i += 1
        return True, volume_list, volume_stop_name
    else:
        return False, datas, "error"


def volume_status_parse_volume(datas, start_pos, end_pos):
    volume = dict()
    # Status of volume
    generate_key_value_pair(volume, datas[start_pos])
    bricks = list()
    brick_base = start_pos + 1
    while '---' in datas[brick_base]:
        brick = dict()
        for i in range(VOLUME_STATUS_BRICK_INFO_LEN):
            generate_key_value_pair(brick, datas[brick_base + i])
        bricks.append(brick)
        brick_base += VOLUME_STATUS_BRICK_INFO_LEN
    volume['bricks'] = bricks
    return volume


def samba_search(volume_name):
    with open('/etc/samba/smb.conf', 'r') as config_file:
        volume_name = '[' + volume_name + ']'
        for line in config_file.readlines():
            if volume_name in line:
                return True
        return False


def execute_samba_on(volume_name):
    path = ' /mnt/'+volume_name
    local_executor.execute('mkdir -p '+path)
    local_executor.execute('chmod 777 -R '+path)
    local_executor.execute('mount -t glusterfs '+CONFIG_LOCAL_HOST+':/'+volume_name+path)
    text = '[' + volume_name + ']\npath=' + path + '\n' + 'writable = yes\n browsable = yes \n guest ok = yes \n'
    with open('/etc/samba/smb.conf', 'a+') as config_file:
        config_file.write(text)
    local_executor.execute('service smb restart')


def execute_samba_off(volume_name):
    with open('/etc/samba/smb.conf', 'r') as read_file:
        with open('/etc/samba/smb.conf.tmp', 'w') as write_file:
            start_delete = False
            volume_name = '['+volume_name+']'
            for line in read_file.readlines():
                if '[' in line:
                    if start_delete:
                        start_delete = False
                    elif volume_name in line:
                        start_delete = True
                if not start_delete:
                    write_file.write(line)
    local_executor.execute('mv /etc/samba/smb.conf.tmp /etc/samba/smb.conf')
    local_executor.execute('service smb restart')


'''
def execute_volume_status(volume_name='all'):
    success, datas = local_executor.execute(VOLUME_STATUS + volume_name + DETAIL, False)
    if success:
        # When there is no volume,command will return 'No volumes present'
        if len(datas) == 1 and ('No volumes present' in datas[0] or 'not started' in datas[0]):
            return False, "Can't get volume status"

        volume_list = list()
        i = 0
        while i < len(datas):
            volume, increment = volume_status_parse_volume(datas, i)
            volume_list.append(volume)
            i += (increment + 1)
        return True, volume_list
    else:
        return False, datas


def volume_status_parse_volume(datas, start_pos):
    #print 'start_pos:   ' + datas[start_pos]
    volume = dict()
    # Status of volume
    generate_key_value_pair(volume, datas[start_pos])
    bricks = list()
    base = start_pos + 1
    while '---' in datas[base]:
        brick = dict()
        for i in range(VOLUME_STATUS_BRICK_INFO_LEN):
            generate_key_value_pair(brick, datas[base + i])
        bricks.append(brick)
        base += VOLUME_STATUS_BRICK_INFO_LEN
    volume['bricks'] = bricks
    return volume, base
'''


def execute_volume_info():
    success, datas = local_executor.execute(VOLUME_INFO, False)
    if success:
        # When there is no volume,command will return 'No volumes present'
        if len(datas) == 1 and 'No volumes present' in datas[0]:
            return False, 'No volumes present'

        volume_list = list()
        i = 0
        while i < len(datas) - 2:
            volume, increment = volume_info_parse_volume(datas, i)
            volume_list.append(volume)
            i += increment
        return True, volume_list
    else:
        return False, datas


def volume_info_parse_volume(datas, start_pos):
    volume = dict()
    for i in range(VOLUME_INFO_LEN_BEFORE_BRICK):
        generate_key_value_pair(volume, datas[start_pos + i])
    if 'x' in volume['Number of Bricks']:
        # disperse volume
        equal_pos = volume['Number of Bricks'].find('=')
        tmp = (volume['Number of Bricks'])[equal_pos + 1:-1]
        block_num = int((volume['Number of Bricks'])[equal_pos + 1:])
    else:
        block_num = int(volume['Number of Bricks'])
    if block_num > 0:
        bricks = dict()
        for i in range(block_num):
            generate_key_value_pair(bricks, datas[start_pos + VOLUME_INFO_LEN_AFTER_BRICK + i])
        volume['Bricks'] = bricks
    end_pos = start_pos + VOLUME_INFO_LEN_AFTER_BRICK + block_num
    while end_pos < len(datas) and 'Volume Name' not in datas[end_pos]:
        generate_key_value_pair(volume, datas[end_pos])
        end_pos += 1
    return volume, end_pos - start_pos - 1


'''
non used:
def execute_local(comamnd):
    p = Popen(comamnd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err == '':
        return True,out
    else:
        return False,err

def execute_pool_list():
    p = Popen([GLUSTER, POOL, 'list'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err == '':
        host_list = list()
        out = out.split('\n')
        del out[0]
        del out[-1]
        for host in out:
            host_dict = dict()
            host = host.split('\t')
            host_dict['hostname'] = host[1].rstrip()
            host_dict['status'] = host[2].strip()
            host_list.append(host_dict)
        return True, host_list
    else:
        return False, err

def generate_dic(string,split_char='\n'):
    result = dict()
    datas = string.split(split_char)
    for data in datas:
        if ':' in data:
            data = data.split(': ')
            result[data[0]] = data[1]
    return result


def execute_normal(cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err == '':
        return True, generate_dic(out)
    else:
        return False,err


def execute_subdict(cmd,subdict_name,subdict_num_line,subdict_start_line,subdict_length):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    result = dict()
    if err == '':
        result['success'] = True
        result['data'] = generate_dic_with_subdict(out, subdict_name, subdict_num_line,subdict_start_line,subdict_length)
    else:
        result['success'] = False
        result['data'] = err
    return result

'''
