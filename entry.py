import config
import datetime
import parser

class Entry:

    def __init__(self,raw_dict):
        # Parse and set metadata
        self.metadata = {}
        parser.set_metadata(self, raw_dict)

    """ Set the group name based on the last guid in guid field by making a request to the API """
    def set_guid_name(self, group_name):
        self.metadata['guid'] = str(group_name)

    """ Return a string of details for the entry """
    def get_details(self):

        string = ""
        string += "\t     -> {} : {}\n".format('File Name', self.metadata['file_name'])
        string += "\t\t{} : {}\n".format('File Path', self.metadata['file_path'])
        string += "\n"
        return string

    def stringify(self):
        string = ""
        string += "\t\t  {}: {}\n".format('File Name', self.metadata['file_name'])
        string += "\t\t  {} : {}\n".format('File Path', self.metadata['file_path'])
        string += "\t\t  {} : {}\n".format('Detection', self.metadata['detection'])
        string += "\n"
        return string

    def stringify_with_count(self, count):
        string = ""
        string += "\t\t  {}: {}\n".format('File Name', self.metadata['file_name'])
        string += "\t\t  {} : {}\n".format('File Path', self.metadata['file_path'])
        string += "\t\t  {} : {}\n".format('Detection', self.metadata['detection'])
        string += "\t\t  {} : {}\n".format('Count', count)
        string += "\n"
        return string
