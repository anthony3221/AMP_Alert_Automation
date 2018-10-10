import requests
import collections
import os
import sys
import datetime
import json
import config
from entry import *
import group_database
from txtfile import sort_by_count_for_summary

""" Api Credentials and details """
auth = config.auth
headers = config.headers
api_endpoint = config.api_endpoint
response_uri = config.response_uri
urlbase_group = config.urlbase_group

""" Connect to api and return a list of all event type"""
def setup_and_connect():

    event_list_uri = response_uri.format(api_endpoint.format('event_types'))
    event_list = requests.get(event_list_uri, headers=headers, auth=auth)

    event_list = event_list.json()
    return event_list

""" List of names for events in detected threat category """
def get_detected_threat_event(): 
    return ['Threat Detected', 'Threat Detected in Exclusion', 'Execution Blocked',
    						 'Rootkit Detection', 'DFC Threat Detected', 'Exploit Prevention']

""" List of names for event in the IOC category """
def get_ioc_event():
    return ['Multiple Infected Files', 'Potential Dropper Infection', 'Java compromise',
    			 'Adobe Reader compromise', 'Microsoft Word compromise', 'Microsoft Excel compromise',
    			 'Microsoft PowerPoint compromise', 'Java launched a shell', 'Adobe Reader launched a shell',
    			 'Microsoft Word launched a shell', 'Microsoft Excel launched a shell', 'Microsoft PowerPoint launched a shell',
    			 'Apple QuickTime compromise', 'Apple QuickTime launched a shell', 'Executed malware',
    			 'Suspected botnet connection', 'Generic IOC', 'Microsoft Calculator compromise',
    			 'Microsoft Notepad compromise', 'Connection to suspicious domain','Threat Detected in Low Prevalence Executable',
    			 'Suspicious Download','Microsoft CHM Compromise',
    			 'Suspicious Cscript Launch', 'Potential Ransomware', 'Possible Webshell']

    
""" Requests all the needed events """
""" Format and parse the returned JSON filed and initialized them as Entry object """
def generate_entry_list():
    detected_threat , ioc = get_filtered_event_list()
    detected_threat_id_list = tuple(detected_threat.values())
    ioc_id_list = tuple(ioc.values())

    # List to store all unparsed events returned 
    raw_event = [] 
    
    #List to store all parsed events
    processed_entry_list = []

    # Params for requests 
    event_uri = response_uri.format(api_endpoint.format('events'))
    dt_params = (('event_type[]', detected_threat_id_list), ("start_date", '{}T00:00:00+00:00'.format(datetime.date.today())))
    ioc_params = (('event_type[]', ioc_id_list), ("start_date", '{}T00:00:00+00:00'.format(datetime.date.today())))
    
    print("Making requests...")
    
    dt_response = requests.get(event_uri, headers=headers, params=dt_params,auth=auth).json()
    ioc_response = requests.get(event_uri, headers=headers, params=ioc_params,auth=auth).json()

    summary = get_summary(dt_response, ioc_response)

    raw_event = dt_response['data'] + ioc_response['data']

    for event_metadata in raw_event: 
        processed_entry = Entry(event_metadata)
        processed_entry_list.append(processed_entry)

    return processed_entry_list, summary

""" Return a string of the summary of total number of all events """
def get_summary(dt_response, ioc_response):
    
    # Event Count dict
    dt_count = {}
    ioc_count = {}

    string = "{}\n\n".format(datetime.date.today())
    string += "Summary:\n"
  
    # Count the number of each event type
    for event in get_detected_threat_event():
        dt_count[event] = 0              
    
    for event in get_ioc_event():                                          
        ioc_count[event] = 0                

    for entry in dt_response['data']: 
        dt_count[entry['event_type']] += 1
                                                                                                 
    for entry in ioc_response['data']:
        ioc_count[entry['event_type']] += 1

    # Build up the string of summary                                                                                    
    string += "\n  Total detected threat event : {}\n\n".format(dt_response["metadata"]["results"]["total"])
    
    dt_count = sort_by_count_for_summary(dt_count)
    for each in dt_count:
        string += "    {} : {}\n".format(each[0], each[-1])
 
    string += "\n"
    string += "\n  Total ioc event : {}\n\n".format(ioc_response["metadata"]["results"]["total"])

    ioc_count = sort_by_count_for_summary(ioc_count)
    for each in ioc_count:
        string += "    {} : {}\n".format(each[0], each[-1])

    string += "\n"
    string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

    return string

""" Filter out wanted event types and return as two dictionaries, one for ioc event and one for detected threat events  """
def get_filtered_event_list():
    response = setup_and_connect()['data']

    detected_threat_dict = {} 
    ioc_dict = {} 
    detected_threat_event = get_detected_threat_event()
    ioc_event = get_ioc_event()
 
    for type in response:
        event_name = type['name']
        if event_name in detected_threat_event: 
            detected_threat_dict[event_name] = type['id']
        if event_name in ioc_event: 
            ioc_dict[event_name] = type['id']

    return detected_threat_dict, ioc_dict


""" Get all group name for each enrtry """
def get_group_name(entry_list): 

    print("\nParsing and getting group name for each entry...\n")

    # Temporary store to minimize communication to database
    temp_store = {}

    for each in entry_list: 
        guid = each.metadata["guid"][-1]
        
        if guid in temp_store: 
            group_name = temp_store[guid]
            each.set_guid_name(group_name)

        else:
            #check if database contain group info 
            if group_database.is_group_exist(guid) == True:
                group_name = group_database.get_group_name(guid)
                each.set_guid_name(group_name)

            #if not make a request and save into database
            else:
                response = make_group_name_request(guid)
                group_name = response['data']['name']
                group_database.insert_new_group(guid, group_name)
                each.set_guid_name(group_name)
    
    return entry_list

""" Make a request to get group name corresponding to the guid """
def make_group_name_request(guid):
    param = config.api_endpoint.format('groups/{}')
    urlbase = config.response_uri.format(param)
    response = requests.get(urlbase.format(guid), headers=config.headers, auth=config.auth).json()

    return response