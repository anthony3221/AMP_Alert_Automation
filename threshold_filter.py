import threshold

"""
Filter class will apply a threshold filtering on all the groups.
It will compare number of all types of event in each host of each group
with the threhsold.

If a host an event type that does not need threshold filtering or the number of an
event type exceeds its limit, the host will be included in the report. For each group,
if no hosts need to be shown in the report, the group will not be shown in the report.
"""
class Filter:

    def __init__(self, group_list):
        self.threshold_store = threshold.get_threshold()
        self.custom_threshold_store = threshold.get_custom_threshold()
        self.filtered_group = list()
        self.unfiltered_group = group_list

    """
    For each group, run filter
    Remove group if no host in the group has any event type exceeding threshold
    Keep the group if a host has an event type exceeding threshold
    """
    def run_threshold_filter(self):

        temp_group_list = list()

        # Run through general threshold        
        for group in self.unfiltered_group:
            if self.check_group_in_general_threshold(group):
                temp_group_list.append(group)

        # Run through custom threshold
        for group in temp_group_list:
            if self.check_group_in_custom_threshold(group):
                self.filtered_group.append(group)

        return self.filtered_group

    """
    Determine if group needs to be included in the report
    Remove the host from group host list if the host has no event type exceeding threshold
    Return false if no host has any event type exceeding threshold
    Return true if a host has an event type exceeding/at threshold
    """
    def check_group_in_general_threshold(self, group):

        included_host = list()
        group.entry_count = 0

        for host in group.host_list:

            if self.check_host_in_general_threshold(host):
                included_host.append(host)
                group.entry_count += host.entry_count

        group.host_list = included_host

        if len(included_host) > 0:
            return True
        else:
            return False

    """
    Determine if the host needs to be included in the report
    Return true if a host has an event type exceeding threshold
    Return false if the host has no event type exceeding threshold
    """
    def check_host_in_general_threshold(self, host):

        for pair in host.event_type:
            event_type = pair[0]
            count = len(pair[1])

            if not event_type in self.threshold_store:
                return True

            else:
                if count >= self.threshold_store[event_type]:
                    return True

            # If host should not be included, decrease the total host entry count.
            host.entry_count -= count

        return False

    def check_group_in_custom_threshold(self, group):
        included_host = list()
        group.entry_count = 0

        for host in group.host_list:

            if self.check_host_in_custom_threshold(host, group.name):
                included_host.append(host)
                group.entry_count += host.entry_count

        group.host_list = included_host

        if len(included_host) > 0:
            return True
        else:
            return False


    ''' Need to check '''
    def check_host_in_custom_threshold(self, host, group_name):

        should_show = True

        for pair in host.event_type:
            event_type = pair[0]
            count = len(pair[1])

            '''
            TODO
            if exist specfic event type in custom threshold:
                check if group_name is in that entry,
                if group_name is that entry:
                    compare count with threshold

                    if count exceed threshold:
                        shown in report
                    else if not exceed threshold but also have other events in custom threshold exceeding
                            the correpsonding threshold / other events not in custom threshold - show in report
                    else dont show

            else keep it included
            '''
            if event_type in self.custom_threshold_store:
                if group_name in self.custom_threshold_store[event_type]:
                    if count >= self.custom_threshold_store[event_type][group_name]:
                        should_show = True
                    else:
                        if len(host.event_type) <= 1:
                            should_show = False

            if not should_show:
                host.entry_count -= count

        return should_show


    """ Return the list of group that need to be display in the report """
    def get_filtered_list(self):
        return self.filtered_group
