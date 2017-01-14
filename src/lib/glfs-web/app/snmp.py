import netsnmp


def snmp_query(oid, dest_host, community,version=2):
    varbind = netsnmp.Varbind(oid)
    result = netsnmp.snmpwalk(varbind, Version=version,
                              DestHost=dest_host, Community=community)
    return result
