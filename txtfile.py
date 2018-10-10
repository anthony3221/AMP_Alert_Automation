import os 
import sys
import datetime
from user_database import connect
from group import *

""" Create and write summary and details of today result in a txt file """
def write_file(summary, entry_list): 
    
    file = open('{}-amp_alert.txt'.format(datetime.date.today()), 'w+')
   
    file.write(summary)

    filtered_and_sorted_group = apply_threshold(entry_list)

    file.write(stringify_group_summary(filtered_and_sorted_group))
    
    file.write(stringify_result(filtered_and_sorted_group)) 
    
    file.close()

def apply_threshold(entry_list):
    sorted_group = sort_by_group(entry_list)

    for each in sorted_group:
        each.apply_threshold()

    return sorted_group

""" Return a list of group sorted in descreasing order of number of entries """
def sort_by_group(entry_list):
    
    # A list of group in decreasing order of their number of entries
    group = [] 

    # Use to store the count of entries for every different group
    group_dict = {}

    for each in entry_list:
        group_dict[each.metadata['guid']] = []

    for each in entry_list:
        group_dict[each.metadata['guid']].append(each)

    for name in group_dict:
        group.append(Group(name, group_dict[name]))
    
    # Sort in terms of the number of entries for each group
    group = sorted(group, key = lambda g : g.entry_count, reverse = True)
    
    return group

""" Return a string of summary of numbers of entries each group has"""
def stringify_group_summary(group_list):
    
    string = "Groups:\n\n"

    index = 1

    for group in group_list: 
        if group.show_in_report == True:
            string += "    {}. ".format(index) 
            string += group.get_summary()

            index += 1
            string += "-----------------------------------------------------------------------------------------------\n"

    return string

""" Return a string of detail for today's result """ 
def stringify_result(group_list):
    
    string = "Details:\n\n"
    index = 1

    for group in group_list:
        if group.show_in_report == True:
            string += "   {} . {} : {}\n".format(index, group.name, group.entry_count)
            string += group.get_details()
            string += "\n"
            string += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            index += 1

    return string 
            
""" Sort the number of entry for each event type (For the general summary in txt file) """
def sort_by_count_for_summary(d):
    
    remove_target = ['Vulnerable Application Detected']
    count = []
    wanted_event = {}

    # Put remove target into end of the list 
    for each in remove_target:
        if each in d:
            count.append(d[each])
            d.pop(each)

    # Remove event type with 0 count
    for each in d:
        if d[each] > 0: 
            wanted_event[each] = d[each]

    wanted_event = sorted(wanted_event.items(), key = lambda kv : kv[1], reverse = True)

    if len(count) > 0:
        for x in range(len(remove_target)):
            wanted_event.append((remove_target[x], count[x]))

    return wanted_event


