import config
import requests
import parser
import database
import datetime

""" API Credentials and endpoints"""
auth = config.auth
headers = config.headers
api_endpoint = config.api_endpoint
response_uri = config.response_uri
urlbase_group = config.urlbase_group

""" Entry / Events """
# Request events
def get_events():
    ioc_ids = tuple(database.get_ioc_events_ids())
    detected_threat_ids = tuple(database.get_detected_threat_ids())

    # Params for requests
    event_uri = response_uri.format(api_endpoint.format('events'))
    dt_params = (('event_type[]', detected_threat_ids),
                 ("start_date", '{}T13:30:00+00:00'.format(get_yesterday())))
    ioc_params = (('event_type[]', ioc_ids),
                  ("start_date", '{}T13:30:00+00:00'.format(get_yesterday())))

    dt_response = requests.get(event_uri,
                               headers=headers,
                               params=dt_params,
                               auth=auth).json()

    ioc_response = requests.get(event_uri,
                                headers=headers,
                                params=ioc_params,
                                auth=auth).json()

    return dt_response['data'] + ioc_response['data']

def get_yesterday():
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
