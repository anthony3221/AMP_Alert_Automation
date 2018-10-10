import os 
import sys 
import gc
from user_database import connect 

""" Return true if the guid exists in the group database """
def is_group_exist(guid):
    conn, c = connect()

    select_query = "SELECT * FROM grouptable WHERE guid = %s"

    c.execute(select_query, str(guid))

    result = c.fetchone()
    
    conn.close()
    gc.collect()
 
    if result:
        return True
    else:
        return False

""" Return the group name of the corresponding guid """
def get_group_name(guid):

    conn, c = connect()
    
    select_query = "SELECT * FROM grouptable WHERE guid = %s"

    c.execute(select_query, str(guid))

    result =  c.fetchone()[-1]
 
    conn.close()
    gc.collect()

    return result 

""" Insert a new guid-group name row into the database """
def insert_new_group(guid, group_name):
    conn , c = connect()

    insert_query = "INSERT INTO grouptable (guid, groupName) VALUES (%s, %s)"

    c.execute(insert_query, (str(guid), str(group_name)))
    
    conn.commit()
    conn.close()
    gc.collect()