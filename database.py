import pymysql
import parser
import gc
import config

GROUP_SELECT_QUERY = "SELECT {} FROM groupTable WHERE {} = %s"
GROUP_INSERT_QUERY = "INSERT INTO groupTable (guid, groupName) VALUES (%s, %s)"
ENTRY_SELECT_QUERY = "SELECT * FROM entryTable WHERE {} = %s and {} = %s and {} = %s and {} = %s"
ENTRY_INSERT_QUERY = "INSERT INTO entryTable (eventID, eventType, date, hostName, fileName, filePath, guid, detection) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
HOST_SELECT_QUERY = "SELECT {} FROM hostTable WHERE {} = %s"
HOST_INSERT_QUERY = "INSERT INTO hostTable (hostName, groupName, IP, networkAddress) VALUES (%s, %s, %s, %s)"
THRESHOLD_INSERT_QUERY = "INSERT INTO eventTypeTable (eventID, eventName, threshold, included) VALUES (%s, %s, %s, %s)"
THRESHOLD_UPDATE_QUERY = "UPDATE eventTypeTable SET {} = %s WHERE {} = %s"
THRESHOLD_SELECT_QUERY = "SELECT {} FROM eventTypeTable WHERE {} = %s"

def connect():
    conn = pymysql.connect(host='localhost',
                           user=config.dbUser,
                           password=config.dbPassword,
                           db='AMP',
                           charset='utf8')
    c = conn.cursor()

    return conn, c

def inject_to_database(entry_list):
    for each in entry_list:
        if not is_entry_exist(each):
            if not is_host_exist(each.metadata["hostname"]):
                host_name = each.metadata["hostname"]
                group_name = each.metadata["guid"]
                IP = each.metadata["external_ip"]
                network_address = each.metadata["network_addresses"]
                insert_new_host(host_name, group_name, IP, network_address)

            insert_new_entry(each)

"""～～～～～～～～～～～～～～～～ Event ～～～～～～～～～～～～～～～～"""
""" ～～～～～～～～～～～～～～～～ Group ～～～～～～～～～～～～～～～～"""
def is_group_exist(guid):
    conn , c = connect()
    query = GROUP_SELECT_QUERY.format("guid", "guid")
    c.execute(query, str(guid))
    res = c.fetchone()
    conn.close()
    gc.collect()

    if res:
        return True
    else:
        return False

""" Return the group name of the corresponding guid """
def get_group_name(guid):
    conn, c = connect()
    query = GROUP_SELECT_QUERY.format("groupName", "guid")
    c.execute(query, str(guid))
    result =  c.fetchone()[-1]

    conn.close()
    gc.collect()

    return result

""" Insert a new guid-group name row into the database """
def insert_new_group(guid, group_name):
    conn , c = connect()
    c.execute(GROUP_INSERT_QUERY, (str(guid), str(group_name)))

    conn.commit()
    conn.close()
    gc.collect()

""" ～～～～～～～～～～～～～～～ Entry ～～～～～～～～～～～～～～～～ """
def insert_new_entry(entry):
    conn, c = connect()
    metadata = entry.metadata

    # Get hostname and guid 
    c.execute("SELECT guid from groupTable where groupName = %s",metadata["guid"])
    guid = c.fetchone()[-1]
    c.execute("SELECT hostName from hostTable where hostName = %s",metadata["hostname"])
    hostname = c.fetchone()[-1]

    arg = (metadata["event_type_id"], metadata["event_type"], metadata["date"],
           hostname,
           metadata["file_name"], metadata["file_path"],
           guid,
           metadata["detection"])

    c.execute(ENTRY_INSERT_QUERY, arg)

    conn.commit()
    conn.close()
    gc.collect()

def is_entry_exist(entry):
    conn , c = connect()
    metadata = entry.metadata
    query = ENTRY_SELECT_QUERY.format("eventType", "hostName","filePath","fileName")
    c.execute(query,(metadata["event_type"], metadata["hostname"], metadata["file_path"], metadata["file_name"]))

    res = c.fetchone()
    conn.close()
    gc.collect()

    if res:
        return True
    else:
        return False

""" ～～～～～～～～～～～～～～～～ Host ～～～～～～～～～～～～～～～～ """
def is_host_exist(hostname):
    conn , c = connect()
    query = HOST_SELECT_QUERY.format("hostName", "hostName")
    c.execute(query, str(hostname))
    res = c.fetchone()
    conn.close()
    gc.collect()

    if res:
        return True
    else:
        return False

# Deprecated method
""" Return the host of the corresponding guid """
def get_host_detail(field,guid):
    conn, c = connect()
    query = HOST_SELECT_QUERY.format("hostName", "hostName")

    c.execute(HOST_SELECT_QUERY.format(str(field)), str(guid))
    result =  c.fetchone()[-1]

    conn.close()
    gc.collect()

    return result

""" Insert a new host into the host table """
def insert_new_host(host_name, group_name, IP, network_address):
    conn , c = connect()
    c.execute(HOST_INSERT_QUERY, (str(host_name), str(group_name), str(IP), str(network_address)))

    conn.commit()
    conn.close()
    gc.collect()

""" ～～～～～～～～～～～～～～ Threshold ～～～～～～～～～～～～～～ """
def insert_new_eventType(eventID, eventName):
    conn, c = connect()
    c.execute(THRESHOLD_INSERT_QUERY, (eventID, str(eventName), 0, 0))

    conn.commit()
    conn.close()
    gc.collect()

def get_eventID(eventName):
    conn, c = connect()
    query = "SELECT {} FROM eventTypeTable WHERE {} = %s".format("eventID", "eventName")
    c.execute(query, str(eventName))

    res = c.fetchone()[-1]

    conn.commit()
    conn.close()
    gc.collect()

    return res

def is_eventType_exist(eventID):
    conn , c = connect()
    c.execute(THRESHOLD_SELECT_QUERY.format("eventID"), eventID)

    res = c.fetchone()
    conn.close()
    gc.collect()

    if res:
        return True
    else:
        return False

def updateEventTypeTable(setCol, setVal, whereCol, whereVal):
    conn, c = connect()
    query = THRESHOLD_UPDATE_QUERY.format(setCol, whereCol)
    c.execute(query, (setVal, whereVal))

    conn.commit()
    conn.close()
    gc.collect()
