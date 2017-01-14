import subprocess
import os
import re
import logging
import sys
from redis_util import *

# Hold a subprocess,write command to it and read response.
class Executor:
    def __init__(self, cmd):
        r, w = os.pipe()
        self.reader = os.fdopen(r)
        sub_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=w, stderr=subprocess.STDOUT)
        self.sub_process = sub_process

    def execute_confirm(self, command):
        if type(command) is not str:
            logging.error("Executor: command type should be str.")
            return False, 'wrong command type'

        self.sub_process.stdin.write('echo y |' + command + '\n')
        result = self.reader.readline()

        if '(y/n)' in result:
            result = re.split('\(y/n\)', result)[1]

        if 'fail' not in result:
            return True, result
        else:
            return False, result

    def execute(self, command, return_str=True):
        if type(command) is not str:
            logging.error("Executor: command type should be str.")
            return False, 'wrong command type'

        # write command
        self.sub_process.stdin.write(command + '\n')
        self.sub_process.stdin.write('echo end\n')

        # read response from stdout/stderr
        if return_str:
            result = self.__read_str()
            # print "hello\n"
            if 'fail' not in result:
                return True, result
            else:
                return False, result
        else:
            result = self.__read_list()
            # print result
            if len(result) == 0:
                return False, 'no content'
            elif 'fail' in result[0]:
                return False, result[0]
            else:
                return True, result

    def __read_str(self):
        result = ""
        while True:
            line = self.reader.readline()
            if line != 'end\n':
                if '(y/n)' not in line:
                    result += line
                else:
                    result += re.split('\(y/n\)', line)[1]
            else:
                break
        return result

    def __read_list(self):
        datas = list()
        while True:
            line = self.reader.readline()
            if line != 'end\n':
                if 'y/n' not in line:
                    datas.append(line)
                else:
                    continue
            else:
                break
        return datas


class LocalExecutor(Executor):
    def __init__(self):
        Executor.__init__(self, ['/bin/bash'])


class SSHExecutor(Executor):
    def __init__(self, remote):
        Executor.__init__(self, ['ssh', '-T', remote])



class View_Executor:
    def execute_confirm(self, command):
        if type(command) is not str:
            logging.error("Executor: command type should be str.")
            return False, 'wrong command type'

        #self.sub_process.stdin.write('echo y |' + command + '\n')
        #result = self.reader.readline()
        Redis.lpush(VIEW_MONITOR, command)
        result = Redis.blpop(MONITOR_VIEW)

        if '(y/n)' in result:
            result = re.split('\(y/n\)', result)[1]

        if 'fail' not in result:
            return True, result
        else:
            return False, result

    def execute(self, command, return_str=True):
        if type(command) is not str:
            logging.error("Executor: command type should be str.")
            return False, 'wrong command type'

        # write command
        #self.sub_process.stdin.write(command + '\n')
        #self.sub_process.stdin.write('echo end\n')
        Redis.lpush(VIEW_MONITOR, (command, return_str))
        result = Redis.blpop(MONITOR_VIEW)

        # read response from stdout/stderr
        if return_str:
            #result = self.__read_str()
            # print "hello\n"
            if 'fail' not in result:
                return True, result
            else:
                return False, result
        else:
            #result = self.__read_list()
            # print result
            if len(result) == 0:
                return False, 'no content'
            elif 'fail' in result[0]:
                return False, result[0]
            else:
                return True, result
