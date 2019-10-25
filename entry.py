import config
import datetime
import parser

"""
An Entry object represents an AMP alert.
The field data is a dictionary which stores the following information about the alert:
    1. Event type ID
    2. Event name
    3. Date
    4. Hostname
    5. File name
    6. File path
    7. Group id
    8. Group name
    10. Detection
"""
class Entry:
    def __init__(self,raw_dict):
        # Parse and set data
        self.data = {}
        parser.set_entry_object_fields(self, raw_dict)

    """ Set the group name """
    def set_guid_name(self, group_name):
        self.data["group_name"] = str(group_name)

    """ Return a string of details for the entry with the count of the entry """
    def stringify_with_count(self, count):
        string = ""
        file_name = self.data["file_name"]
        file_path = self.data["file_path"]
        detection = self.data["detection"]

        string += "\t\t  {}: {}\n".format("File Name", file_name)
        string += "\t\t  {} : {}\n".format("File Path", file_path)
        string += "\t\t  {} : {}\n".format("Detection", detection)
        string += "\t\t  {} : {}\n".format("Count", count)
        string += "\n"
        return string
