import requests
import config
import datetime

class Entry:
    
    def __init__(self, raw_dict):

        if 'computer' in raw_dict:
            self.computer = raw_dict['computer']
        else: 
            self.computer = {}

        if 'date' in raw_dict:
            self.date = raw_dict['date']
        else:
            self.date = datetime.date.today()

        if 'event_type' in raw_dict:
            self.event_type = raw_dict['event_type']
        else:
            self.event_type = "Unknown"

        if 'file' in raw_dict:
            self.file = raw_dict['file']
        else: 
            self.file = {}
        
        if 'group_guids' in raw_dict:
            self.group_guids = raw_dict['group_guids']
        else:
            self.group_guids = {}

        self.metadata = {} 

	# Parse and set metadata
        self.set_metadata()

    """ Parse and set metadata """
    def set_metadata(self):

        self.metadata["event_type"] =  self.event_type
        self.metadata["date"] = self.date
        self.metadata["guid"] = self.group_guids

        self.process_metadata()

    """ Parse data from the 'computer' and 'file' and store into metadata dictionary """
    def process_metadata(self):
        wanted_field_in_computer = ['external_ip', 'hostname', 'network_addresses']
        wanted_field_in_file = ['file_name','file_path']

        for field in wanted_field_in_computer:
            if field in self.computer:
                self.metadata[field] = self.computer[field]
            else:
                self.metadata[field] = "Unknown"

        for field in wanted_field_in_file:
            if field in self.file:
                self.metadata[field] = self.file[field]
            else:
                self.metadata[field] = "Unknown"

        if self.file != {}:

            if 'identity' in self.file:
                if 'sha256' in self.file["identity"]:
                    self.metadata['sha256'] = self.file["identity"]['sha256']
                else:
                    self.metadata['sha256'] = "Unknown"
            else:
                self.metadata['sha256'] = "Unknown"

        if self.file == {}:
            self.metadata['sha256'] = "Unknown"


    """ Set the group name based on the last guid in guid field by making a request to the API """
    def set_guid_name(self, group_name):
        self.metadata['guid'] = str(group_name)

    """ Return the metadata dictionary """
    def get_metadata(self):
        return self.metadata

    """ Return a string of details for the entry """
    def get_details(self):

        string = ""
        string += "\t     -> {} : {}\n".format('File Name', self.metadata['file_name'])
        string += "\t\t{} : {}\n".format('File Path', self.metadata['file_path'])
        string += "\t\t{} : {}\n".format('SHA256', self.metadata['sha256'])
        string += "\n"
        return string
