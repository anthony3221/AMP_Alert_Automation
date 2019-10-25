import config
import requests
import parser
import datetime

""" API Credentials and endpoints"""
auth = config.auth
headers = config.headers
api_endpoint = config.api_endpoint
response_uri = config.response_uri
urlbase_group = config.urlbase_group

""" Entry / Events """
# Return a list of event id of IOC events 
def get_ioc_id():
    return [1107296257,1107296258,1107296261,1107296262,1107296263,
            1107296264,1107296266,1107296267,1107296268,1107296269,
            1107296270,1107296271,1107296272,1107296273,1107296274,
            1107296275,1107296276,1107296277,1107296278,1107296280,
            1107296281,1107296282,1107296283,1107296284]

# Return a list of event id of Detected Threat events 
def get_detected_threat_id():
    return [1090519054,553648168,1090519081,1090519084,1090519103,
            1090519105,1090519112]

"""
Return two dictionaries (key:event id, value: event type), one for ioc,
one for detected threats
"""
def get_event_type_id_dict():
    json = request.get_event_list()
    detected_threat_dict = {}
    ioc_dict = {}
    ioc_id = request.get_ioc_id()
    detected_threat_id = request.get_detected_threat_id()

    for type in json:
        id = type['id']
        if id in ioc_id:
            ioc_dict[type["name"]] = id
        if id in detected_threat_id:
            detected_threat_dict[type["name"]] = id

    return ioc_dict, detected_threat_dict

# Connect to api endpoint and return a list of event type 
def get_event_list():
	uri = response_uri.format(api_endpoint.format('event_types'))
	event_list = requests.get(uri, headers=headers, auth=auth)
	event_list = event_list.json()
	return event_list['data']

# Request events
def get_events():
    ioc, detected_threatc = get_event_type_id_dict()
    detected_threat_id_list = tuple(detected_threat.values())
    ioc_id_list = tuple(ioc.values())

    # Params for requests
    event_uri = response_uri.format(api_endpoint.format('events'))
    dt_params = (('event_type[]', detected_threat_id_list),
                 ("start_date", '{}T13:30:00+00:00'.format(getYesterday())))
    ioc_params = (('event_type[]', ioc_id_list),
                  ("start_date", '{}T13:30:00+00:00'.format(getYesterday())))

    dt_response = requests.get(event_uri,
                               headers=headers,
                               params=dt_params,auth=auth).json()
    ioc_response = requests.get(event_uri,
                                headers=headers,
                                params=ioc_params,auth=auth).json()

    return dt_response['data'] + ioc_response['data']

def getYesterday():
    return (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')

""" Group """
# Make a request to get group name corresponding to the guid 
def request_group_name(guid):
    param = api_endpoint.format('groups/{}')
    urlbase = response_uri.format(param)
    response = requests.get(urlbase.format(guid),
                            headers=headers,
                            auth=auth).json()

    group_name = response['data']['name']
    return group_name
