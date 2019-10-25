import collections
from host import *

""" A Group object represents a group that an alert comes from. """
class Group:
    def __init__(self, name, entry_list):
        self.name = name
        self.entries = entry_list
        self.host_list = []
        self.entry_count = 0

        # Sort by host in the group
        self.sort_by_hostname()

    """
    Group entries of the group by host name. Create a Host object for each unique host
    and store in a list. Sort the host list by the number of entries in each host in
    descending order.
    """
    def sort_by_hostname(self):
        host_dict = collections.defaultdict(list)

        for each in self.entries:
            hostname = each.data["hostname"]
            host_dict[hostname].append(each)

        sorted_by_hostname = sorted(host_dict.items(), key = lambda kv: len(kv[1]), reverse = True)

        for each in sorted_by_hostname:
            hostname = each[0]
            entries = each[1]
            ip = entries[0].data['external_ip']
            network_address= entries[0].data['network_addresses']

            self.host_list.append(Host(hostname, ip, network_address, entries))

    """ Return a string containing details of each entry """
    def stringify(self):
        string = ""
        string += "\tGroup : {}\n".format(self.name)
        string += "\tNumber of alerts : {}\n".format(self.entry_count)
        string += "\tNumber of hosts: {}\n".format(len(self.host_list))

        for host in self.host_list:
            string += "\t    Host: {}\n".format(host.name)
            string += "\t    IP: {}\n".format(host.ip)
            string += "\t    Network Address: {}\n\n".format(host.network_address)
            string += host.stringify()

        return string
