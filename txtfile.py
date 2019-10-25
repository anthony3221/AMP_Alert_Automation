import os
import sys
import datetime
import database
import parser
from group import *
from threshold_filter import *

""" Create and write summary and details of today result in a txt file """
def generate_report(entry_list):

    file = open('{}-amp_alert.txt'.format(datetime.date.today()), 'w+')

    # Overall count
    overall_count = parser.get_summary(entry_list)

    # Sort group count
    sorted_group_list = sort_by_group(entry_list) # List of groups
    sorted_by_host_count = count_by_host(sorted_group_list) # Sorted by number of host in group


    # Apply threshold filtering 
    filter = Filter(sorted_by_host_count)

    print("Applying threshold")
    filter.run_threshold_filter()

    filtered_group_list = filter.get_filtered_list()

    # Stringify Summary
    general_summary = stringify_overall_summary(overall_count)
    group_summary = stringify_group_summary(filtered_group_list)

    # Stringify Details
    details = stringify_details(filtered_group_list)

    # Write to report
    file.write(general_summary)
    file.write(group_summary)
    file.write(details)

    file.close()

""" Create and return a overall summary """
def stringify_overall_summary(count):

    string = ""
    string += "AMP Report: {}\n\n".format(datetime.date.today())
    string += "Overall Summary:\n"

    for each in count:
        string += "\t{} : {}\n".format(each[0], each[1])

    string += "\n"
    return string

""" Create and return a overall summary """
def stringify_group_summary(group_list):

    string = ""
    string += "Group Summary (Number of Host/Group):\n"

    for group in group_list:
        string += "\t{} : {}\n".format(group.name, len(group.host_list))

        for host in group.host_list:
            string += "\t    Host: {}\n".format(host.name)

            for eventType in host.event_type:
                string += "\t\t{} ({})\n".format(eventType[0], len(eventType[-1]))

            string += "\n"

    string += "\n"
    return string

""" Sort groups by the number of host in the group """
def count_by_host(sorted_group_list):
    return sorted(sorted_group_list, key = lambda kv : len(kv.host_list), reverse = True)

""" Sort all entries into groups according to group id """
def sort_by_group(entry_list):
    group_dict = dict()
    group_list = []

    for each in entry_list:
        group = each.metadata["guid"]

        if not group in group_dict:
            group_dict[group] = []

        group_dict[group].append(each)

    group_dict = sorted(group_dict.items(), key = lambda kv : len(kv[1]), reverse = True)

    for each in group_dict:
        name = each[0]
        entry_list = each[1]
        group_list.append(Group(name, entry_list))

    return group_list

""" Return a string of details for each event in each group for each host """
def stringify_details(group_list):
    string = "Details:\n"

    for each in group_list:
        string += each.stringify()
        string += "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"

    return string
