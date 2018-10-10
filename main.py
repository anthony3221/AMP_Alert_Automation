#! /usr/bin/python3

import config
import entry_database
import parse
import notify
import txtfile

if __name__ == '__main__':
    # 1. Set up and Get data
    parse.setup_and_connect()

    # 2. Parse data and Store data   
    entry_list, summary = parse.generate_entry_list()
    
    entry_list = parse.get_group_name(entry_list)
     
    entry_database.inject_to_entry_database(entry_list)
    
    #3. Notify

    txtfile.write_file(summary, entry_list)

    recipient = notify.recipient

    for each in recipient:
        notify.send_email(each)

    """ TO-DO LIST """   
    #1. Error handling 
    #2. Notification System
        # Group into 1/2 emails
        # Send out notification
