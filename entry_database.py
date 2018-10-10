from user_database import connect
import datetime
from entry import *
import gc

""" Check for duplicate entry in the entry table in the database """
def check_for_duplicate(conn, c, metadata):
    select_query = "SELECT * FROM entry WHERE eventType = %s AND groupName = %s AND hostName = %s AND externalIp = %s AND networkAddress = %s AND fileName = %s AND filePath = %s"
    
    event_type = metadata["event_type"]
    group_name = metadata["guid"]
    host_name = metadata["hostname"]
    external_ip = metadata["external_ip"]
    network_addresses = metadata["network_addresses"]
    file_name = metadata["file_name"]
    file_path = metadata["file_path"]

    arg = (event_type, group_name, host_name, external_ip, network_addresses, file_name, file_path)
    c.execute(select_query, arg)

    result = c.fetchall()
    if result : 
        return True 
    else: 
        return False

""" Return the date at of a certain entry """
# def get_entry_date(entry):
	
#     select_query = "SELECT * FROM entry WHERE eventType = %s AND groupName = %s AND hostName = %s AND externalIp = %s AND networkAddress = %s AND fileName = %s AND filePath = %s"
# 	#metadata = entry.metadata

# 	eventType = entry.metadata['event_type']
# 	groupName = entry.metadata['guid']
# 	hostName = entry.metadata['hostname']
# 	externalIp = entry.metadata['external_ip']
# 	networkAddress = entry.metadata['network_addresses']
# 	fileName = entry.metadata['file_name']
# 	filePath = entry.metadata['file_path']

#     arg = (event_type, group_name, host_name, external_ip, network_addresses, file_name, file_path)
#     c.execute(select_query, arg)

# 	result = c.fetchall()

# 	if result:
# 		return result["date"]
# 	else : 
# 		return None

""" Compare timestamps, return date difference in terms of day """
def get_date_difference(date): 
	pass

""" Insert new entry to the entry table in the database """
def add_entry_to_database(conn, c, entry_metadata):	

	insert_query = "INSERT INTO entry (eventType, date, groupName, hostName, externalIp, networkAddress, fileName, filePath, SHA256) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

	eventType = str(entry_metadata['event_type'])
	date = entry_metadata['date']
	groupName = str(entry_metadata['guid'])
	hostName = str(entry_metadata['hostname'])
	externalIp = str(entry_metadata['external_ip'])
	networkAddress = str(entry_metadata['network_addresses'])
	fileName = str(entry_metadata['file_name'])
	filePath = str(entry_metadata['file_path'])
	sha256 = str(entry_metadata['sha256'])

	c.execute(insert_query, (eventType,date,groupName,hostName,externalIp,networkAddress,fileName,filePath,sha256))
	conn.commit()
	gc.collect()

""" Helper method to stringify network addresses metadata """
def stringify_network_address(network_addresses):
	string = ""
	for dict_element in network_addresses:
		string += "{"
		for key , value in dict_element.items():
			if value == "":
				value = "Unknown"
			string += "{}:{} ".format(key,value)
		string += "} "

	return string

""" Helper method to format today's date """
def format_date(): 
	 return datetime.date.today()

""" Check for duplicate in the database, insert new entry if no duplicate found """
def inject_to_entry_database(entry_list):
	conn, c = connect()
	insert_count = 0
	print("Updating entry database...")
	for entry in entry_list:

		entry_metadata = entry.get_metadata()
		entry_metadata['date'] = format_date()
		entry_metadata['network_addresses'] = stringify_network_address(entry_metadata['network_addresses'])
		
		entry_exist = check_for_duplicate(conn, c, entry_metadata)
		if (entry_exist == False):
                    add_entry_to_database(conn, c, entry_metadata)
                    insert_count += 1

	print("Finish updating entry database.")
	print("{} new entries were inserted".format(insert_count))
	conn.commit()
	conn.close()
	gc.collect()

""" Check if the alert is a duplicate in a one week time period """
# def entry_in_week_period(entry_list):

# 	conn ,c = connect()

# 	result = []

# 	for each in entry_list:
# 		metadata = each.metadata
		
# 		if check_for_duplicate(conn, c, metadata):
# 			flag_date = get_entry_date(each)

# 			if get_date_difference(flag_date) >= 7:
# 				# Add to today's entry
# 				result.append(each) 
# 				# Renotify

# 	return result


		



