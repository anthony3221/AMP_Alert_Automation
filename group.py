from host import *

""" Class for group from the result of today """
class Group:

    def __init__(self, name, entry_list):

        self.name = name
        self.members = entry_list
        self.host_list = []
        self.entry_count = len(self.members)

        # Sort by host in the group
        self.sort_by_hostname()
        self.show_in_report = False

    def apply_threshold(self):
        for each in self.host_list:
            each.apply_threshold()
        
        self.show_in_report = self.should_display_in_file()

    def should_display_in_file(self):

        for each in self.host_list:
            if each.show_in_report == True:
                return True
                
        return False
    
    """ Sort all the entries from this group by host """
    def sort_by_hostname(self):
        
        self.host_list = []

        # Use to store the count of entries for each host      
        host_count = {}
        # Use to store the the entry object of each host
        host_event = {} 

        for each in self.members:
            
            name = each.metadata['hostname']
            host_event[name] = []
            host_count[name] = 0

        for each in self.members:

            name = each.metadata['hostname']
            host_event[name].append(each)
            host_count[name] += 1

        # Sort by the number of event of each host in decreasing order
        host_count = sorted(host_count.items(), key = lambda kv : kv[1], reverse = True)

        for each in host_count:
    
            name = str(each[0])
            # A big list of host in decreasing order of their number of entry
            self.host_list.append(Host(name, host_event[name]))

        # # Sort in terms of the event type for each host
        # for each in self.host_list:
        #     each.sort_by_event_type()

    """ Return a string for a short summary of total number of entry for different host for the group """
    def get_summary(self):
        string = ""
        
        string += "{}\n".format(self.name, self.entry_count)
        string += "       Number of entry : {}\n".format(self.entry_count)
        string += "       Number of different host : {}\n\n".format(len(self.host_list))
        string += "       Host:\n"

        for host in self.host_list:
            if host.show_in_report == True:
                string += host.get_summary()
                
        string += "\n"

        return string 

    """ Return a string for a detailed description of all entries of the group """
    def get_details(self):
        
        index = 'A'
        string = ""
        string += "\n      Host:\n"
        for each in self.host_list:
            if each.show_in_report == True:
                string += "\t{}.".format(index)
                string += " {} : {}\n".format(each.name, each.entry_count)
                string += each.get_details()

                index = chr(ord(index) + 1)
            
        return string

