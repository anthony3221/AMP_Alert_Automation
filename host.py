import collections

""" A Host object represents a host that flagged an alert. """
class Host :
    def __init__(self, name, ip, network_address, entry_list):
        self.name = name
        self.ip = ip
        self.network_address = network_address
        self.entries = entry_list
        self.entry_count = 0
        self.event_type = collections.defaultdict(list)

        # Sort by event type of this host
        self.sort_by_event_type()

    """
    Group entries of this host by event type and sort in descending order
    according to number of each event type.
    """
    def sort_by_event_type(self):
        for entry in self.entries:
            event_type = entry.data['event_type']
            self.event_type[event_type].append(entry)

        self.event_type = sorted(self.event_type.items(), key=lambda x : len(x[-1]), reverse=True)

    """ Return a string for a short summary of total number of each event types for the host """
    def stringify(self):
        string = ""

        for each in self.event_type:
            string += self.entry_summary_string(each[0], each[-1])

        return string

    """
    Return a string that represents a summary of entry details of an event type with the
    count of each different entry.
    """
    def entry_summary_string(self, event_type, list_of_event):
        string = ""
        count = collections.defaultdict(list)

        # Sort by file name to avoid duplicated event.
        for each in list_of_event:
            file_name = each.data["file_name"]
            count[file_name].append(each)

        string += "\t      Event Type: {} ({})\n\n".format(event_type, len(list_of_event))

        for entry_list in count.values():
            entry = entry_list[-1]
            count = len(entry_list)
            string += entry.stringify_with_count(count)

        return string
