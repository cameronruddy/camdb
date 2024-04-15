'''
For importing things from a csv (such as gps)
and adding them to an existing metadata file

Stores data as a list of dictionary entries
csvpath and fields to read from are passed to import data

TODO: Have option to make copy of old metadata file

'''

import csv, os, sys, json
import pdb
import color_scheme as clr
import dir_crawler as dc
from misc_tools import time_handler as th, meta_modify as mm

DEFAULT_FIELDS = ["Measurement_DateTime", "GPS_lat", "GPS_lon"]
TIME_TOLERANCE = 1.0 # In seconds

class csv2meta:

    def __init__(self, verbose):
        self.verbose = verbose

    def import_data(self, csvpath, fields):
        self.data = []
        with open(csvpath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                payload = {f:row[f] for f in fields}
                self.data.append(payload)

    def check_type(self, string):
        string = string.split()
        if len(string) == 1:
            string = string[0]
            if string == "true" or string == "True":
                return True
            elif string == "false" or string == "False":
                return False
            elif string == "null" or string == "None":
                return None

            try:
                return float(string)
            
            except ValueError:
                pass

            return string
        else:
            return string


    def add2meta(self, metapath, time_vec_mapping, **kwargs):

        # If the input is a file, just add new data to this one file
        if os.path.isfile(metapath):    
            target_paths = [metapath]

        # If input is a directory, iterate over the entire list
        elif os.path.isdir(metapath):
            session = dc.dir_crawler(metapath,
                                     "",
                                     "",
                                     ".json",
                                     False)
            session.traverse()
            session.reorganize()
            target_paths = session.printout()
            del session

        # path is not valid, exit
        else:
            print("{}Error{}: Supplied path {}{}{} is not a valid file or dictionary".format(
                clr.ERROR, clr.RESET,
                clr.HIGHLIGHT, metapath, clr.RESET
            ))
            return 1    #TODO: handle this in main.py

        field_vec_mappings = kwargs         # just renaming this to make more sense
        #time_tool = th.time_handler()
        meta_tool = mm.meta_modify(self.verbose)
        csv_time_ID = time_vec_mapping[0]   # What is the time field called in original CSV file?
        out_time_ID = time_vec_mapping[1]   # What is the time field called in output file?

        
        for out_path in target_paths:
            with open(out_path, 'r') as f:
                current_metadata = json.load(f)
            
            # Exit if the time ID is not in the provided metadata
            if out_time_ID not in current_metadata.keys():
                print("{}Error{}: Provided key {}{}{} is not found in {}{}{}".format(
                    clr.ERROR, clr.RESET,
                    clr.HIGHLIGHT, out_time_ID, clr.RESET,
                    clr.HIGHLIGHT, out_path, clr.RESET
                ))   
                return 1    # TODO: have main.py handle this

            # provided key is in metadata
            # iterate over every row in the csv log

            # get the timestamp in the output file as a float for arithmetic
            outfile_time = float(current_metadata[out_time_ID])
            for csv_row in self.data:
                # get next csv timestamp as a float for arithmetic
                try:
                    csv_time = float(th.utc2epoch(csv_row[csv_time_ID]))
                except ValueError:
                    csv_time = float(csv_row[csv_time_ID])

                # if the current csv row is within 1s of the outfile's timestamp, writeout
                if outfile_time > (csv_time - TIME_TOLERANCE) and outfile_time < (csv_time + TIME_TOLERANCE):
                    for field in field_vec_mappings.keys():
                        # See if there are sub keys
                        try:
                            for sub_field in field_vec_mappings[field].keys():
                                current_metadata[field][sub_field] = self.check_type(
                                    csv_row[field_vec_mappings[field][sub_field]])
                                if self.verbose:
                                    print("{}Writing{}: Field: {}, Value: {}, to {}{}{}".format(
                                        clr.SUCCESS, clr.RESET,
                                        field_vec_mappings[field][sub_field],
                                        current_metadata[field][sub_field],
                                        clr.HIGHLIGHT, out_path, clr.RESET 
                                    ))
                        except AttributeError:
                            current_metadata[field] = self.check_type(
                                csv_row[field_vec_mappings[field]])
                            if self.verbose:
                                print("{}Writing{}: Field: {}, Value: {}, to {}{}{}".format(
                                    clr.SUCCESS, clr.RESET,
                                    field_vec_mappings[field],
                                    current_metadata[field],
                                    clr.HIGHLIGHT, out_path, clr.RESET
                                ))
                    with open(out_path, 'w') as f:
                        json.dump(current_metadata, f, indent=5)
                    break


    def printout(self):
        for item in self.data:
            print(item["GPS_lat"])


if __name__ == "__main__":
    session = csv2meta()
    session.import_data("/home/rfal/projects/wriva/gps_parse_dev/GPSL0005copy.CSV",
                        DEFAULT_FIELDS)
    session.printout()