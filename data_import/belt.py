import sys, os, json, pprint
from colorama import Fore, Back, Style
from datetime import datetime
from data_import import make_meta, make_label

import color_scheme as clr

class belt:
    item_paths = []
    out_paths = []
    verbose = False

    config = {}
    last_dir_name = ""
    meta_tools = {}
    labels = {}

    def __init__(self, config_path, item_path, out_root, verbose):
        self.out_root = out_root
        self.config_path = config_path
        self.verbose = verbose

        # Read in file paths. If input is list, basically a passthough
        if type(item_path) == list:
            self.item_paths = item_path
        elif os.path.isfile(item_path):
            with open(item_path) as f:
                self.item_paths = [line[:-1] for line in f]
        
        # Open Config
        try:
            with open(config_path) as f:
                self.config = json.load(f)
        except TypeError:
            self.view_edit()
            return

        try:
            if self.config["cameras"] == {}:
                print("{}Warning{}: Specified config file {} has no camera information".format(
                    clr.WARNING, clr.RESET,
                    config_path
                ))
                if input("Manually enter camera information [y/n]: ") == 'y':
                    self.view_edit(input("Enter an ID for this camera: "))
                else: sys.exit(0)

            for cam_name in self.config["cameras"]:
                try:
                    self.labels[cam_name] = make_label.make_label(**{
                        "site_name": self.config["label"]["site_name"],
                        "site_desc": self.config["label"]["site_desc"],
                        "deliv_date": self.config["label"]["deliv_date"],
                        "test_time": "",
                        "camera_name": cam_name,
                        "camera_desc": self.config["cameras"][cam_name]["camera_desc"],
                        "out_root": out_root
                    })
                except KeyError as e:
                    self.view_edit(cam_name)

                try:
                    with open(self.config["cameras"][cam_name]["config"], 'r') as f:
                        self.meta_tools[cam_name] = (
                            make_meta.make_meta(**json.load(f))
                        )
                except FileNotFoundError:
                    print("{}Warning{}: Could not find camera configuration file in {}".format(
                        clr.WARNING, clr.RESET,
                        config_path
                    ))
                    if input("Continue without camera configuration? [y/n]: ") == 'y':
                        self.meta_tools[cam_name] = make_meta.make_meta()
                    else: sys.exit(1)
        except KeyError:
            print("{}Warning{}: no camera information found in {}".format(
                Fore.YELLOW, Fore.RESET,
                self.config_path
            ))
            source = input("Enter a camera name to continue or exit: ")
            if source != "exit":
                self.view_edit(source)
            else:
                sys.exit(0)

    def view_edit(self, cam_name):
        user_input = ""
        
        self.labels[cam_name] = make_label.make_label()
        try:
            self.labels[cam_name].data["out_root"] = self.out_root
            self.labels[cam_name].data["test_time"] = ""
            self.labels[cam_name].data["camera_name"] = cam_name
            self.labels[cam_name].data["site_name"] = self.config["label"]["site_name"]
            self.labels[cam_name].data["site_desc"] = self.config["label"]["site_desc"]
            self.labels[cam_name].data["deliv_date"] = self.config["label"]["deliv_date"]
            self.labels[cam_name].data["camera_desc"] = self.config["cameras"][cam_name]["camera_desc"]
            
        except KeyError:
            pass

        self.meta_tools[cam_name] = make_meta.make_meta()
        for key in self.meta_tools[cam_name].data.keys():
            try:
                self.meta_tools[cam_name].update_field(**{key: self.config["metadata"][key]})
            except KeyError:
                continue

        while(user_input != "exit"):
            os.system("clear")
            print("Current label for {}: \n{}".format(
                cam_name,
                self.labels[cam_name].get_whole_path()
            ))
            print("Current label fields:")
            pprint.pprint(self.labels[cam_name].data)
            current_keys = self.labels[cam_name].data.keys()
            user_input = input("\nSpecify field to edit or \"exit\": ")
            if user_input in current_keys:
                new_value = input(
                    "Modify \"{}\" from \"{}\" to: ".format(
                        user_input,
                        self.labels[cam_name].data[user_input]
                    )
                )
                self.labels[cam_name].data[user_input] = new_value

    def time_string(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d-%H-%M-%S")

    def parse_dirname(self, path, file):
        change_dir = False
        dirname = os.path.dirname(path)

        if self.last_dir_name != dirname:
            self.last_dir_name = dirname
            change_dir = True

            for cam_name in self.labels:
                self.labels[cam_name].file_idx = 1
                self.labels[cam_name].set_test_time(self.get_starttime(file))
                if not os.path.exists(self.labels[cam_name].abspath):
                    os.makedirs(self.labels[cam_name].abspath)
        
        return change_dir
