import os
import sys
import datetime
import collections
import database
import parser
from group import *
from threshold_filter import *

""" Create and write summary and details of today result in a txt file """
def generate_report(entry_list):
    file = open('{}-amp_alert.txt'.format(datetime.date.today()), 'w+')

    # Overall count
    overall_count_summary = parser.get_summary(entry_list)

    # Sort group count
    sorted_group_list = sort_by_group(entry_list) # List of groups

    # Apply threshold filtering 
    filter = Filter(sorted_group_list)
    print("Applying threshold")
    filter.run_threshold_filter()
    filtered_group_list = filter.get_filtered_list()

    # Stringify Summary
    general_summary = stringify_overall_summary(overall_count_summary)
    group_summary = stringify_group_summary(filtered_group_list)

    # Special instruction applicable to groups in entry list
    groups = set([group.name for group in filtered_group_list])
    special_instructions = get_special_instructions(groups)

    # Stringify Details
    details = stringify_details(filtered_group_list)

    # Write to report
    file.write(general_summary)
    file.write(group_summary)
    file.write(special_instructions)
    file.write(details)
    file.close()

""" Create and write error report into a txt file """
def generate_err_report(exception):
    fname = "{}-AMP_Crash_Log.txt".format(datetime.date.today())
    file = open(fname, 'w+')
    file.write("{}\n".format(datetime.date.today()))
    file.write("{}\n".format(str(exception)))
    file.close()

""" Create and return a overall summary """
def stringify_overall_summary(count):
    string = "AMP Report: {}\n\n".format(datetime.date.today())
    string += "Overall Summary:\n"

    for each in count:
        event_type = each[0]
        count = each[1]
        string += "\t{} : {}\n".format(event_type, count)

    string += "\n"
    return string

""" Create and return a overall summary """
def stringify_group_summary(group_list):
    string = "Group Summary (Number of Host/Group):\n"

    for group in group_list:
        string += "\t{} : {}\n".format(group.name, len(group.host_list))

        for host in group.host_list:
            string += "\t    Host: {}\n".format(host.name)

            for event_type in host.event_type:
                string += "\t\t{} ({})\n".format(event_type[0], len(event_type[-1]))

            string += "\n"

    return string

""" Sort all entries into groups according to group name """
def sort_by_group(entry_list):
    group_dict = collections.defaultdict(list)
    group_list = []

    for entry in entry_list:
        group_name = entry.data["group_name"]
        group_dict[group_name].append(entry)

    for group_name in group_dict:
        entry_list = group_dict[group_name]
        group_list.append(Group(group_name, entry_list))

    # Sort by number of host in each group
    group_list = sorted(group_list, key=lambda kv : len(kv.host_list), reverse=True)
    return group_list

""" Return a string of special instructions applicable to certain groups. """
def get_special_instructions(group_names):
    group_instructions = dict()

    for group_name in group_names:
        instructions = database.get_group_special_instructions(group_name)
        if instructions:
            group_instructions[group_name] = instructions

    if len(group_instructions) > 0:
        string = "Special Instructions:\n"
        for group_name, instructions in group_instructions.items():
            string += "\t{}: {}\n".format(group_name, instructions)
        string += "\n"
        return string

    return ""

""" Return a string of details for each event in each group for each host """
def stringify_details(group_list):
    string = "Details:\n"

    for group in group_list:
        string += group.stringify()
        string += "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"

    return string
