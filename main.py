import parser
import database
import txtfile
import notify
import datetime
import os

if __name__ == '__main__':
    try:
        os.chdir(os.path.abspath("/data/applications/AMP"))

        # Request, parse, get a list of AMP alerts.
        entry_list = parser.generate_entry_list()
        print("Successfully got and parsed data")

        # Save data to database.
        database.save_to_database(entry_list)
        print("Successfully inserted data to database")

        # Generate report in form of a .txt file to display all alerts.
        txtfile.generate_report(entry_list)
        print("Successfully generated report")

        # Send out the report through an email.
        notify.send_report()
        print("Successfully sent report")
        print("Completed")

    except Exception as e:
        # Send out the crash report through an email.
        txtfile.generate_err_report(e)
        notify.send_crash_report()
        print("Error Encountered, see crash log")
