import Threshold

""" Class for host in each different group"""

class Host : 
    def __init__(self, name, entry_list):
        self.name = name 
        self.members = entry_list
        self.entry_count = len(entry_list)

        # For later use in sorting 
        self.sorted_members = []
        self.event_type_count = {}
        self.event = {}

        # Sort by event type of this host
        self.sort_by_event_type()
        self.show_in_report = True


    def apply_threshold(self):

        threshold = Threshold.THRESHOLD
        
        for each in self.event_type_count:
            #Fix Here
            # if the specific event does not meet the threshold, no need to show in report
            if each[0] in threshold and each[1] < threshold[each[0]]:
                del self.event[each[0]]

        self.show_in_report = self.should_display_in_file()

    def should_display_in_file(self):
        if self.event != {}:
            return True
        else:
            return False

    """ Sort all the entries from this host by event type """
    def sort_by_event_type(self):

        # Use to store the count of each event type
        event_type_count = {}
        # Use to store the the entry object of each event type
        event = {}

        for each in self.members:

            event_type = str(each.metadata['event_type'])
            event[event_type] = []
            event_type_count[event_type] = 0 
        
        for each in self.members:

            event_type = str(each.metadata['event_type'])
            event[event_type].append(each)
            event_type_count[event_type] += 1

        # Sort by the numeber of each event type in decreasing order
        self.event_type_count = sorted(event_type_count.items(), key = lambda kv : kv[1], reverse = True)
        
        for each in self.event_type_count: 
            event_type = each[0]
            # A long list of entries in decreasing order of numbers of event type
            self.sorted_members += event[event_type]
        
        # A dictionary of events in which key : name of event type, value : list of entry object of the correpsonding event type
        # For stringify the details later
        self.event = event 

    """ Return a string for a short summary of total number of each event types for the host """
    def get_summary(self):
        string = "" 

        for each in self.event:

            # Ignore if the event type vulnerable application detected
            string += "          {}:  ".format(self.name)
            string += "\n\t     {} : {}\n".format(each, len(self.event[each]))

        return string
        
    """ Return a string for a detailed description of all entries of the host except 'Vulnerable Application Detected' """
    def get_details(self):
        
        string = ""
        index = 'a'

        for each in self.event_type_count:
            event_type = each[0]

            if event_type in self.event:
                string += "\n          {}. ".format(index)
                string += "{} : {}\n".format('Event Type', event_type)
                string += "\t     {} : {}\n".format('External IP', self.event[event_type][0].metadata['external_ip'])
                string += "\t     {} : {}\n".format('Network Address', self.event[event_type][0].metadata['network_addresses'])
                string += "\n"

                for entry in self.event[event_type]:
                    string += entry.get_details()
                    break
                
                index = chr(ord(index) + 1)

        return string 
