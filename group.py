from host import *

""" Class for group from the result of today """
class Group:

    def __init__(self, name, entry_list):

        self.name = name
        self.entries = entry_list
        self.host_list = []
        self.entry_count = 0

        # Sort by host in the group
        self.sort_by_hostname()

    def sort_by_hostname(self):

        host_dict = dict()

        for each in self.entries:
            hostname = each.metadata["hostname"]

            if not hostname in host_dict:
                host_dict[hostname] = []

            host_dict[hostname].append(each)

        sorted_by_hostname = sorted(host_dict.items(), key = lambda kv: len(kv[1]), reverse = True)

        for each in sorted_by_hostname:
            name = each[0]
            entries = each[1]
            ip = entries[0].metadata['external_ip']
            networkAddress= entries[0].metadata['network_addresses']

            self.host_list.append(Host(name, ip, networkAddress, entries))

    def stringify(self):
        string = ""
        string += "\tGroup : {}\n".format(self.name)
        string += "\tNumber of alerts : {}\n".format(self.entry_count)
        string += "\tNumber of hosts: {}\n".format(len(self.host_list))

        for each in self.host_list:
            string += "\t    Host: {}\n".format(each.name)
            string += "\t    IP: {}\n".format(each.ip)
            string += "\t    Network Address: {}\n\n".format(each.networkAddress)

            string += each.stringify()

        return string

    def getHostNum(self):
        return len(self.host_list)

