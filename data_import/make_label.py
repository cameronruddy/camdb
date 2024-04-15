import json
from datetime import datetime

class make_label:   
    
    #template_path = "configuration/label_config.json"
    
    
    def __init__(self, **kwargs):
        self.data = {
            "site_name": "",
            "site_desc": "",
            "deliv_date": "",
            "test_time": "",
            "camera_name": "",
            "camera_desc": "",
            "out_root": ""
        }                  
        self.abspath = ""               # Absolute path to current file
        self.filename = ""              # Name of current file
        self.file_idx = 1               # output file index

        if kwargs:
            for key in kwargs:
                if key in self.data.keys():
                    self.data[key] = kwargs[key]    

        self.config_abspath()
        self.config_filename()

    # Manually update fields
    def update_field(self, **kwargs):
        for key in kwargs:
            if key in self.data:
                self.data[key] = kwargs[key]

    # dt is expected as a number
    def set_test_time(self, secs):
        dt = datetime.fromtimestamp(secs)
        dt = dt.strftime("%Y-%m-%d-%H-%M-%S")
        self.data["test_time"] = dt

        # Refresh names
        self.config_abspath()
        self.config_filename()

    def set_frame_num(self, num):
        self.file_idx = num

    def config_abspath(self):
        self.abspath = "{}/{}-{}-delivery/{}-{}/{}-{}/{}/".format(
                        self.data["out_root"],
                        self.data["deliv_date"],
                        self.data["site_name"],
                        self.data["site_name"],
                        self.data["site_desc"],
                        self.data["camera_name"],
                        self.data["camera_desc"],
                        self.data["test_time"])
                        
        return self.abspath

    def config_filename(self, *args):
        if args:
            #self.current_file_num = args[0]
            self.file_idx = args[0]

        self.filename = "{}-{}-{}-{:08d}".format(
                        self.data["site_name"],
                        self.data["camera_name"],
                        self.data["test_time"],
                        self.file_idx)
        
        return self.filename
    
    def get_whole_path(self, *args):

        if args:
            self.file_idx = args[0]

        self.config_abspath()
        self.config_filename()
        return self.abspath + self.filename

    def print_config(self):
        print(self.out_root, self.site_name, self.camera_name)


if __name__ == "__main__":

    session = make_label(1695324412)    # Test date
    print(session.print_whole_path())