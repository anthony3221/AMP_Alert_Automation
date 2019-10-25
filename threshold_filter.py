import database
"""
Filter class will apply a threshold filtering on all the groups.
It will compare number of all types of event in each host of each group
with the threhsold.

If a host has an event type that does not need threshold filtering or the number of an
event type exceeds its limit, the host will be included in the report. For each group,
if no hosts need to be shown in the report, the group will not be shown in the report.
"""
class Filter:
    def __init__(self, group_list):
        self.threshold_store = database.get_threshold()
        self.custom_threshold_store = database.get_custom_threshold()
        self.filtered_group = list()
        self.unfiltered_group = group_list

    """
    For each group, run filter
    Remove group if no host in the group has any event type exceeding threshold
    Keep the group if a host has an event type exceeding threshold
    """
    def run_threshold_filter(self):
        # List used to store groups that have been filtered through general threshold
        temp_group_list = list()

        # Run each group through general threshold.
        for group in self.unfiltered_group:
            # For SEO group, always include those in the report
            if "-SEO-" in group.name:
                temp_group_list.append(group)
                group.entry_count = len(group.entries)
            elif self.apply_general_threshold_on_group(group):
                temp_group_list.append(group)

        # Run each group through custom threshold.
        # Each group presumably has at least one host which has at least one event type
        # which exceeds the corresponding general threshold.
        for group in temp_group_list:
            if "-SEO-"in group.name:
                self.filtered_group.append(group)
            elif self.apply_custom_threshold_on_group(group):
                self.filtered_group.append(group)

        return self.filtered_group

    """
    This function determines if group needs to be included in the report.
    Remove the host from group host list if the host has no event type exceeding threshold.
    Return false if there is no host which contains an event type which exceeds
    the corresponding threshold. Return true if there exists a host in the group which has
    an event type exceeding its corresponding threshold
    """
    def apply_general_threshold_on_group(self, group):
        included_host = list()

        for host in group.host_list:
            if self.apply_general_threshold_on_host(host):
                included_host.append(host)

        group.host_list = included_host

        return len(included_host) > 0

    """
    This functions determines if the host needs to be included in the report.
    Return true if the host has an event type exceeding the corresponding threshold.
    Return false if the host has no event type exceeding the corresponding threshold.
    """
    def apply_general_threshold_on_host(self, host):
        # host.event_type is a list of tuple, where the first element is the event_type name,
        # and the second element is the list of Entry objects for the corresponding event_type.
        for pair in host.event_type:
            event_type = pair[0]
            count = len(pair[1])

            # If the event type does not have a threshold, include the host in the report.
            if not event_type in self.threshold_store:
                return True
            # If the count of the event type exceeds the threshold, include the host in the report.
            else:
                if count >= self.threshold_store[event_type]:
                    return True

        return False

    def apply_custom_threshold_on_group(self, group):
        included_host = list()

        for host in group.host_list:
            if self.apply_custom_threshold_on_host(host, group.name):
                included_host.append(host)
                group.entry_count += host.entry_count

        group.host_list = included_host

        return len(included_host) > 0

    def apply_custom_threshold_on_host(self, host, group_name):
        # To keep track of whether specific event type exceeds the threshold.
        exceed_threshold = dict()

        for pair in host.event_type:
            event_type = pair[0]
            count = len(pair[1])
            host.entry_count += count
            # First we assume that the event type exceeds its threshold.
            exceed_threshold[event_type] = True

            # If there is a threshold for the group on the specific event type
            # and the count for that event type in this host is below the threshold,
            # do not include and decrease the entry count for the host.
            if event_type in self.custom_threshold_store:
                if group_name in self.custom_threshold_store[event_type]:
                    if count < self.custom_threshold_store[event_type][group_name]:
                        exceed_threshold[event_type] = False
                        host.entry_count -= count

        # Return if any of the event type exceeds its threshold, i.e. should be shown in the report.
        return any(exceed_threshold.values())

    """ Return the list of group that need to be display in the report """
    def get_filtered_list(self):
        return self.filtered_group
