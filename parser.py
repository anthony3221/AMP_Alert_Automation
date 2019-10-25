import requests
import json
import collections
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

""" Return a list of all events """
def generate_entry_list():
    processed_entry_list = list()

    # Make a request to get all alerts.
    events = request.get_events()

    for data in events:
        processed_entry = Entry(data)
        processed_entry_list.append(processed_entry)

    # For each Entry, look up the group name for the corresponding guid.
    set_group_name_for_entries(processed_entry_list)

    return processed_entry_list

""" Get and set the group name for each entry. """
def set_group_name_for_entries(entry_list):
    group_names = dict()

    for each in entry_list:
        if not each.data["group_guids"]:
            each.set_group_name("No group is associated for this event")

        # Always use the last item in group guids list to look up the group name
        guid = each.data["group_guids"][-1]

        if guid in group_names:
            group_name = group_names[guid]
            each.set_guid_name(group_name)
        else:
            group_name = request.request_group_name(guid)
            group_names[guid] = group_name
            database.insert_or_update_group(group_name, guid)
            each.set_guid_name(group_name)

""" Parse and set data field in Entry object from a given raw dictionary returned by the API """
def set_entry_object_fields(entry, raw_dict):
    fields = ["event_type_id", "event_type", "detection", "group_guids", "computer", "file"]

    for field in fields:
        if field in raw_dict:
            entry.data[field] = raw_dict[field]
        else:
            entry.data[field] = None

    # Set date field for the entry
    entry.data["date"] = datetime.date.today()

    # Further parsing 
    process_fields(entry)

    # Set None fields to "Unknown"
    handle_none_fields(entry)

""" Helper methods to further parse out data """
def process_fields(entry):
    computer_attr = ["external_ip", "hostname", "network_addresses"]
    file_attr = ["file_name", "file_path"]

    for field in computer_attr:
        if not entry.data["computer"]:
            entry.data[field] = None
            continue

        if field in entry.data["computer"]:
            entry.data[field] = entry.data["computer"][field]
        else:
            entry.data[field] = None

    for field in file_attr:
        if not entry.data["file"]:
            entry.data[field] = None
            continue

        if field in entry.data["file"]:
            entry.data[field] = entry.data["file"][field]
        else:
            entry.data[field] = None

    # Stringify network address
    if entry.data["network_addresses"]:
        network_addresses = entry.data["network_addresses"]
        entry.data["network_addresses"] = stringify_network_address(network_addresses)

""" Set None fields in Entry object to 'Unknown' """
def handle_none_fields(entry):
    fields = ["event_type_id", "event_type", "detection", "group_guids",
              "external_ip", "hostname", "network_addresses", "file_name",
              "file_path"]

    for field in fields:
        if not entry.data[field]:
            entry.data[field] = "Unknown"

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

"""
Count the number of event for each different event type.
Return a dictionary where the key is the name of an event type,
and the value is the count of the event type.
"""
def get_summary(entry_list):
    count = collections.defaultdict(int)

    for each in entry_list:
        event_type = each.data["event_type"]
        count[event_type] += 1

    # Sort the dict by count of each event type in descending order
    count = sorted(count.items(),
                   key = lambda kv : kv[1],
                   reverse = True)

    return count
