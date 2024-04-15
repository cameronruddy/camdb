import shutil
import os, sys, json
import color_scheme as clr
from data_import.belt import belt

class copy_import(belt):

    def __init__(self, config_path, item_path, out_root, verbose):
        belt.__init__(self, config_path, item_path, out_root, verbose)

    def get_starttime(self, filepath):
        try:
            with open(filepath, 'r') as f:
                temp_data = json.load(f)
            return temp_data["timestamp"]
        except:
            print("{}Warning{}: No timestamp information found in {}{}{}".format(
                clr.WARNING, clr.RESET,
                clr.HIGHLIGHT, filepath, clr.RESET
            ))
            user_input = ""

            while user_input != "exit":
                user_input = input("Please enter a time in epoch time or exit: ")
                try:
                    return float(user_input)
                except ValueError:
                    print("{}Warning{}: Invalid entry".format(
                        clr.WARNING, clr.RESET
                    ))
            sys.exit(1)

    def copy_relabel(self, filename):
        # First see if there is an associated metadata file
        # If so, try to read timestamp info from that metadata file
        # Then, try to read the source from the metadata file
        # If metadata file, see if there's a source in a config file
        # If neither, ask for user input

        text, ext = os.path.splitext(filename)
        source_dir = os.path.dirname(filename)

        if os.path.isfile(text + ".json"):
            metafile = text + ".json"
            belt.parse_dirname(self, metafile, metafile)
        else:
            metafile = None
            belt.parse_dirname(self, filename, filename)    # This will prompt the user for timestamp info

        source = None
        if metafile:
            try:
                with open(metafile, 'r') as f:
                    temp_data = json.load(f)
                source = temp_data["source"]
                if source == {}: raise KeyError

            except:
                print("{}Warning{}: cannof find a camera name in {}{}{}".format(
                    clr.WARNING, clr.RESET,
                    clr.HIGHLIGHT, metafile, clr.RESET
                ))

        if os.path.isfile(self.config_path) and not source:

            try:
                source = self.config["cameras"]
                if source == {}:
                    raise KeyError

            except KeyError:
                print("{}Warning{}: cannot find a camera name in {}{}{}".format(
                    clr.WARNING, clr.RESET,
                    clr.HIGHLIGHT, self.config_path, clr.RESET
                ))
        if not source:
            source = input("Please enter a camera name: ")

        try:
            img_copy = shutil.copyfile(
                filename,
                (str(self.labels[source].get_whole_path()) + ext)
            )
            print("{}Copied{} {}{} {}to{} {}".format(
                clr.SUCCESS, clr.RESET,
                source_dir, filename,
                clr.SUCCESS, clr.RESET,
                img_copy 
            ))

            json_copy = shutil.copyfile(
                #source_dir + '/' + self.labels[source].filename + ".json",
                metafile,
                (str(self.labels[source].get_whole_path()) + ".json")
            )
            print("{}Copied{} {}{}.json {}to{} {}".format(
                clr.SUCCESS, clr.RESET,
                source_dir, text, 
                clr.SUCCESS, clr.RESET,
                json_copy
            ))

        except FileNotFoundError:
            if self.verbose:
                print("{}Warning{}: No metadata file found for {}{}{}".format(
                    clr.WARNING, clr.RESET,
                    clr.HIGHLIGHT, filename, clr.RESET
                ))
                print("Making metadata file with name {}{}{}".format(
                    clr.HIGHLIGHT, (str(self.labels[source].get_whole_path()) + '.json'), clr.RESET
                ))
            self.meta_tools[source].update_field(**{
                "fname":(str(self.labels[source].filename) + ext),
                "source": source
            })
            self.meta_tools[source].writeout(
                str(self.labels[source].get_whole_path())
            )
        
        self.labels[source].file_idx += 1

    def run_belt(self):
        
        for item in self.item_paths:

            self.copy_relabel(item)