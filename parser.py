import requests
import json
import config
import database
import request
from entry import *

""" API Credentials and endpoints"""
auth = config.auth
headers = config.headers
api_endpoint = config.api_endpoint
response_uri = config.response_uri
urlbase_group = config.urlbase_group

def get_summary(entry_list):
    count_store = {}

    for each in entry_list:
        if not each.metadata["event_type"] in count_store:
            count_store[each.metadata["event_type"]] = 1
        else:
            count_store[each.metadata["event_type"]] += 1

    count_store = sorted(count_store.items(),
                         key = lambda kv : kv[1],
                         reverse = True)

    return count_store

""" Entry """
# Parse and set metatdata for Entry Object
def set_metadata(entry, raw_dict):
    if "event_type_id" in raw_dict:
        entry.metadata["event_type_id"] = raw_dict["event_type_id"]
    else:
        entry.metadata["event_type_id"] = "Unknown"

    if 'event_type' in raw_dict:
        entry.metadata["event_type"] = raw_dict['event_type']
    else:
        entry.metadata["event_type"] = "Unknown"

    if 'detection' in raw_dict:
        entry.metadata["detection"] = raw_dict["detection"]
    else:
        entry.metadata["detection"] = "Unknown"

    entry.metadata["date"] = datetime.date.today()

    if 'group_guids' in raw_dict:
        entry.metadata["guid"] = raw_dict['group_guids']
    else:
        entry.metadata["guid"] = {}

    # Further parsing 
    if 'computer' in raw_dict:
        computer_raw_dict= raw_dict['computer']
    else:
        computer_raw_dict = {}

    if 'file' in raw_dict:
        file_raw_dict= raw_dict['file']
    else:
        file_raw_dict = {}

    process_metadata(entry, computer_raw_dict, file_raw_dict)

# Helper Method
def process_metadata(entry, computer_raw_dict, file_raw_dict):
    wanted_field_in_computer = ['external_ip', 'hostname', 'network_addresses']
    wanted_field_in_file = ['file_name','file_path']

    for field in wanted_field_in_computer:
        if field in computer_raw_dict:
            entry.metadata[field] = computer_raw_dict[field]
        else:
            entry.metadata[field] = "Unknown"

    for field in wanted_field_in_file:
        if field in file_raw_dict:
            entry.metadata[field] = file_raw_dict[field]
        else:
            entry.metadata[field] = "Unknown"

    if "network_addresses" in entry.metadata:
        entry.metadata["network_addresses"] = stringify_network_address(entry.metadata["network_addresses"])


""" Return a list of all needed events """
def generate_entry_list():
    # List to store all parsed events
    parsed_entry_list = []

    raw_event = request.get_events()

    for event_metadata in raw_event:
        processed_entry = Entry(event_metadata)
        parsed_entry_list.append(processed_entry)

    parsed_entry_list = get_group_name(parsed_entry_list)

    return parsed_entry_list


""" Get all group name for each enrtry """
def get_group_name(entry_list):
    # Temporary store for caching
    temp_store = {}

    for each in entry_list:
        guid = each.metadata["guid"][-1]

        if guid in temp_store:
            group_name = temp_store[guid]
            each.set_guid_name(group_name)
        else:
            #check if database contain group info
            if database.is_group_exist(guid) == True:
                group_name = database.get_group_name(guid)
                each.set_guid_name(group_name)
            #if not make a request and save into database
            else:
                group_name = request.request_group_name(guid)
                database.insert_new_group(guid, group_name)
                each.set_guid_name(group_name)

    return entry_list

""" Stringify the network addresses """
def stringify_network_address(network_addresses):
    string = ""
    for dict_element in network_addresses:
        string += "{"
        for key , value in dict_element.items():
            if value == "":
                value = "Unknown"
            string += "{}:{} ".format(key,value)
        string += "}"

    return string
