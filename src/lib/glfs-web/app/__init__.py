from command import *
from views import app
from monitor import Monitor
from command_execute import execute_samba_on


if __name__ == '__main__':
    refresh_snapshots()
    # samba_on('volume-snapshot')
    # run = sh.Command('/bin/umount')
    # print run('/brick/brick1')
    # query_periodically()
    '''
    storage_descr = snmp_query('hrStorageDescr', 'tfs01', 'public')
    storage_size = snmp_query('hrStorageSize', 'tfs01', 'public')
    storage_used = snmp_query('hrStorageUsed', 'tfs01', 'public')
    logging.warning(storage_descr)
    logging.warning(storage_size)
    logging.warning(storage_used)
    '''