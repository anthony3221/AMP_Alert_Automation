import config
import parser
import database
import json
import txtfile
import notify
import datetime
import os

if __name__ == '__main__':

    try:
        os.chdir(os.path.abspath("/data/applications/AMP"))

        # Get and parse data
        entry_list = parser.generate_entry_list()
        print("Successfully got and parsed data")

        # Insert data
        database.inject_to_database(entry_list)
        print("Successfully inserted data to database")

        # Display data
        txtfile.generate_report(entry_list)
        print("Successfully generated report")

        # Send Email
        notify.send_report()
        print("Successfully sent report")
        print("Completed")

    except Exception as e:
        fname = "{}-AMP_Crash_Log.txt".format(datetime.date.today())
        file = open(fname, 'w+')
        file.write("{}\n".format(datetime.date.today()))
        file.write("{}\n\n".format(str(e)))
        file.close()
        notify.send_crash_report()
        print("Error Encountered, see crash log")
