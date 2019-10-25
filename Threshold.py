import database
import request
import gc

""" Methods for initializing and setting up threshold database """
def updateEventTypeTable():
    event_list = request.get_event_list()

    for each in event_list:
        eventID = each['id']
        eventName = each['name']
        print(eventID)
        if not database.is_eventType_exist(eventID):
            database.insert_new_eventType(eventID, eventName)

def setThreshold(eventID, threshold):
    if database.is_eventType_exist(eventID):
        database.updateEventTypeTable("threshold", threshold, "eventID", eventID)

def modifyEntryTable():
    conn, c = database.connect()

    c.execute("SELECT DISTINCT eventType from entryTable")

    res = c.fetchall()

    for each in res:
        print(each)
        print(each[0])
        c.execute("SELECT eventID from eventTypeTable WHERE eventName=%s", each)
        res = c.fetchone()[-1]
        query = "update entryTable SET eventID = %s where eventType = %s"
        c.execute(query,(str(res),str(each[0])))
    conn.commit()
    conn.close()
    gc.collect()

def setIncluded():
    ioc_list = request.get_ioc_id()
    detected_threat_list = request.get_detected_threat_id()

    for each in ioc_list:
        if database.is_eventType_exist(each):
            print(each)
            database.updateEventTypeTable("included", 1, "eventID", each)

    for each in detected_threat_list:
        if database.is_eventType_exist(each):
            print(each)
            database.updateEventTypeTable("included", 1, "eventID", each)

""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
"""
Return a dictionary of event-type-threshold-limit pair

key : event_type
value : threshold limit of that event type
"""
def get_threshold():
    conn, c = database.connect()

    c.execute("SELECT eventName, threshold from eventTypeTable where threshold > 0")

    res = c.fetchall()

    threshold_store = dict()

    for each in res:
        threshold_store[each[0]] = each[1]

    conn.close()
    gc.collect()

    return threshold_store

def get_custom_threshold():
    conn, c = database.connect()

    c.execute("SELECT * FROM thresholdExceptionTable")

    res = c.fetchall()

    exceptionThreshold = dict()

    for each in res:
        threshold = each[1]
        group_name = each[3]
        event_name = each[4]

        if not event_name in exceptionThreshold:
            exceptionThreshold[event_name] = dict()

        exceptionThreshold[event_name][group_name] = threshold

    conn.close()
    gc.collect()

    return exceptionThreshold
