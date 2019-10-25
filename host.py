""" Class for host in each different group"""
class Host :
    def __init__(self, name, ip, networkAddress, entry_list):
        self.name = name
        self.ip = ip
        self.networkAddress = networkAddress
        self.entries = entry_list
        self.entry_count = len(self.entries)
        self.event_type = dict()

        # Sort by event type of this host
        self.sort_by_event_type()

    """ Sort all the entries from this host by event type """
    def sort_by_event_type(self):

        for entry in self.entries:
            eventType = entry.metadata['event_type']
            if not eventType in self.event_type:
                self.event_type[eventType] = list()

            self.event_type[eventType].append(entry)

        self.event_type = sorted(self.event_type.items(), key = lambda x : len(x[-1]))

    """ Return a string for a short summary of total number of each event types for the host """
    def stringify(self):
        string = ""

        for each in self.event_type:
            string += self.entry_summary_string(each[0], each[-1])

        return string


    """ Return a string that represents a summary of entry details of an event type without duplicate """
    def entry_summary_string(self, event_type, list_of_entries):

        string = ""
        entry_store = dict()
        entry_count = dict()

        for each in list_of_entries:
            file_name = each.metadata['file_name']

            if not file_name in entry_store:
                entry_store[file_name] = each
                entry_count[file_name] = 1

            else:
                entry_count[file_name] += 1

        string += "\t      Event Type: {} ({})\n\n".format(event_type, len(list_of_entries))

        for fname in entry_count:
            entry = entry_store[fname]
            count = entry_count[fname]
            string += entry.stringify_with_count(count)

        return string
