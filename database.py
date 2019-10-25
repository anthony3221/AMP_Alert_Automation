import pymysql
import parser
import request
import gc
import config

""" Query to run in database """
GROUP_SELECT_ALL_QUERY= "SELECT * from groupTable"
GROUP_UPDATE_QUERY = "UPDATE groupTable SET groupName = %s WHERE guid = %s AND groupName <> %s"
GROUP_SELECT_QUERY = "SELECT {} FROM groupTable WHERE {} = %s"
GROUP_INSERT_QUERY = "INSERT INTO groupTable (guid, groupName) VALUES (%s, %s)"
ENTRY_SELECT_QUERY = "SELECT * FROM entryTable WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s AND {} = %s AND {} = %s"
ENTRY_INSERT_QUERY = "INSERT INTO entryTable (eventID, eventType, date, hostName, fileName, filePath, guid, detection) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
HOST_SELECT_QUERY = "SELECT {} FROM hostTable WHERE {} = %s"
HOST_INSERT_QUERY = "INSERT INTO hostTable (hostName, groupName, IP, networkAddress) VALUES (%s, %s, %s, %s)"
EVENT_TYPE_SELECT_QUERY = "SELECT * from eventTypeTable"
EVENT_TYPE_UPDATE_NAME_QUERY = "UPDATE eventTypeTable SET eventName = %s WHERE eventID = %s AND eventName <> %s"
THRESHOLD_INSERT_QUERY = "INSERT INTO eventTypeTable (eventID, eventName, threshold, included, is_ioc, is_detected_threat) VALUES (%s, %s, %s, %s, FALSE, FALSE)"
THRESHOLD_UPDATE_QUERY = "UPDATE eventTypeTable SET {} = %s WHERE {} = %s"
THRESHOLD_SELECT_QUERY = "SELECT {} FROM eventTypeTable WHERE {} = %s"
GENERAL_THRESHOLD_SELECT_ALL_QUERY = "SELECT eventName, threshold from eventTypeTable where threshold > 0"
CUSTOM_THRESHOLD_SELECT_ALL_QUERY = "SELECT * FROM thresholdExceptionTable"
SPECIAL_INSTRUCTIONS_SELECT_QUERY = "SELECT {} FROM specialInstructionsTable WHERE {} = %s"

""" Given a list of entry, save each into database. """
def save_to_database(entry_list):
    for entry in entry_list:
        # Update event type in db if necessary.
        event_type_id = entry.data["event_type_id"]
        event_type = entry.data["event_type"]
        insert_or_update_event_type(event_type_id, event_type)

        # Insert new host if does not existi.
        if not is_host_exist(entry.data["hostname"]):
            host_name = entry.data["hostname"]
            group_name = entry.data["group_name"]
            IP = entry.data["external_ip"]
            network_address = entry.data["network_addresses"]
            insert_new_host(host_name, group_name, IP, network_address)

        # Insert new entry if does not exist.
        if not is_entry_exist(entry):
            insert_new_entry(entry)

""" Connect to the database. Return a connection and cursor object. """
def connect():
    conn = pymysql.connect(host='localhost',
                           user=config.db_user,
                           password=config.db_password,
                           db='AMP',
                           charset='utf8')
    c = conn.cursor()
    return conn, c

"""～～～～～～～～～～～～～～～～～～ Event ～～～～～～～～～～～～～～～～～～"""

"""
Look up a event type with the given event type id. If no such event type exist,
add to database. If an event type exist but the current names does not match with
the given event type name, update to use the new name.
"""
def insert_or_update_event_type(event_type_id, event_type):
    conn, c = connect()
    select_query = THRESHOLD_SELECT_QUERY.format("*", "eventID")
    insert_query = THRESHOLD_INSERT_QUERY
    update_query = EVENT_TYPE_UPDATE_NAME_QUERY

    res = c.execute(select_query, str(event_type_id))
    if not res:
        c.execute(insert_query, (str(event_type_id), str(event_type), 0, 0))
    else:
        c.execute(update_query, (str(event_type), str(event_type_id), str(event_type)))

    conn.commit()
    conn.close()
    gc.collect()

""" Return a list of IOC event type id """
def get_ioc_events_ids():
    conn, c = connect()
    query = THRESHOLD_SELECT_QUERY.format("eventID", "is_ioc")
    c.execute(query, str(int(True)))
    res = c.fetchall()
    ioc = [each[0] for each in res]
    conn.close()
    gc.collect()

    return ioc
""" Return a list of detected threat event type id """
def get_detected_threat_ids():
    conn, c = connect()
    query = THRESHOLD_SELECT_QUERY.format("eventID", "is_detected_threat")
    c.execute(query, str(int(True)))
    res = c.fetchall()
    detected_threat = [each[0] for each in res]
    conn.close()
    gc.collect()

    return detected_threat

""" ～～～～～～～～～～～～～～～～～～ Group ～～～～～～～～～～～～～～～～～～"""

"""
Look up a group with the given guid. If no such group exist, add to
database. If a group exist but the current group name does not match with the
given group name, update to use the new name.
"""
def insert_or_update_group(group_name, guid):
    conn, c = connect()
    insert_query = GROUP_INSERT_QUERY
    select_query = GROUP_SELECT_QUERY.format("*", "guid")
    update_query = GROUP_UPDATE_QUERY

    res = c.execute(select_query, str(guid))
    if not res:
        c.execute(insert_query, (str(guid), str(group_name)))
    else:
        c.execute(update_query, (str(group_name), str(guid), str(group_name)))

    conn.commit()
    conn.close()
    gc.collect()

""" ～～～～～～～～～～～～～～～～～ Entry ～～～～～～～～～～～～～～～～～～ """

""" Add a new entry to the database. """
def insert_new_entry(entry):
    conn, c = connect()
    data = entry.data
    event_type_id = str(data["event_type_id"])
    event_type = str(data["event_type"])
    date = str(data["date"])
    hostname = str(data["hostname"])
    file_name = str(data["file_name"])
    file_path = str(data["file_path"])
    guid = str(data["group_guids"][-1])
    detection = str(data["detection"])
    arg = (event_type_id, event_type, date, hostname,
           file_name, file_path, guid, detection)
    c.execute(ENTRY_INSERT_QUERY, arg)
    conn.commit()
    conn.close()
    gc.collect()

"""
Look up if there is an existing entry in the database. Duplicated
entries should share the same event type, hostname, file path, file name,
detection of the same day.
"""
def is_entry_exist(entry):
    conn , c = connect()
    query = ENTRY_SELECT_QUERY.format("eventType", "hostName", "date",
                                      "filePath", "fileName", "detection")
    event_type = str(entry.data["event_type"])
    hostname = str(entry.data["hostname"])
    date = str(entry.data["date"])
    file_path = str(entry.data["file_path"])
    file_name = str(entry.data["file_name"])
    detection = str(entry.data["detection"])
    arg = (event_type, hostname, date, file_path, file_name, detection)
    c.execute(query, arg)
    res = c.fetchall()
    conn.close()
    gc.collect()

    return res if res else None

""" ～～～～～～～～～～～～～～～～～～ Host ～～～～～～～～～～～～～～～～～～ """

""" Look up if a host with the given hostname already exists in the database."""
def is_host_exist(hostname):
    conn , c = connect()
    query = HOST_SELECT_QUERY.format("hostName", "hostName")
    c.execute(query, str(hostname))
    res = c.fetchall()
    conn.close()
    gc.collect()

    return res if res else None

""" Add a new host into the database """
def insert_new_host(host_name, group_name, IP, network_address):
    conn, c = connect()
    arg = (str(host_name), str(group_name), str(IP), str(network_address))
    c.execute(HOST_INSERT_QUERY, arg)
    conn.commit()
    conn.close()
    gc.collect()

""" ～～～～～～～～～～～～～～～～ Threshold ～～～～～～～～～～～～～～～～ """

"""
Return a dictionary of where,

key: event type
value: threshold limit of that event type.

{
  Cloud IOC : 10,
  Executed Malware : group_C : 10
}
"""
def get_threshold():
    conn, c = connect()
    query = GENERAL_THRESHOLD_SELECT_ALL_QUERY
    c.execute(query)
    res = c.fetchall()
    threshold_store = {each[0] : each[1] for each in res}
    conn.close()
    gc.collect()

    return threshold_store

"""
Return a dictionary of custom threshold where,

key: event type
value: a dictionary where the key is group name and the value is
       the threshold for the event.

e.g.
{
 Cloud IOC: { group_A : 10,
               group_B : 20 },
  Executed Malware : { group_A : 4,
                       group_C : 10 }
}
"""
def get_custom_threshold():
    conn, c = connect()
    query = CUSTOM_THRESHOLD_SELECT_ALL_QUERY
    c.execute(query)
    res = c.fetchall()
    custom_threshold = dict()

    for each in res:
        threshold = each[1]
        group_name = each[3]
        event_name = each[4]

        if not event_name in custom_threshold:
            custom_threshold[event_name] = dict()

        custom_threshold[event_name][group_name] = threshold

    conn.close()
    gc.collect()

    return custom_threshold
""" ～～～～～～～～～～～～～～～～ Threshold ～～～～～～～～～～～～～～～～ """

""" Get special instructions for the given group name (if any). """
def get_group_special_instructions(group_name):
    conn, c = connect()
    group_select_query = GROUP_SELECT_QUERY.format("guid", "groupName")
    c.execute(group_select_query, str(group_name))
    res = c.fetchone()

    if not res:
        return ""

    guid = res[0]
    get_special_instructions_query = SPECIAL_INSTRUCTIONS_SELECT_QUERY.format("*", "guid")
    c.execute(get_special_instructions_query, str(guid))
    res = c.fetchone()
    if res:
        return res[1]

    return ""
