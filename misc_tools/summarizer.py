import json, os, sys
import pprint
import color_scheme as clr
from view_edit import view_edit

class summarizer(view_edit):
    
    def __init__(self, targets):
        try:
            with open(targets, 'r') as f:
                self.target_list = [line[:-1] for line in f]
        except TypeError:
            self.target_list = targets
        try:
            first_path = self.target_list[0]
        except TypeError:
            first_path = self.target_list

        with open(first_path, 'r') as f:
            data = json.load(f)
        view_edit.__init__(self, data)
    
    def action(self, key):
        # Probably a better way to do this
        if key not in self.data:
            return
        
        value_path_pairs = {}
        for path in self.target_list:
            with open(path, 'r') as f:
                temp_data = json.load(f)
            try:
                value_path_pairs.append({temp_data[key]:path})
            except:
                continue

        unique_values = []
        for val_path_pair in value_path_pairs:
            temp = next(iter(val_path_pair))
            if temp not in unique_values:
                unique_values.append(temp)

        num_unique_values = len(unique_values)
        if num_unique_values >= 10:
            if input("Print all {} values in {}? [y/n]".format(
                num_unique_values,
                key
            )) != 'y':
                return

        os.system("clear")
        for value in unique_values:
            print(value)
        
        user_input = ""
        while user_input != "return" or user_input != "r":
            user_input = input("Enter {}where{} to show filename(s) of specified value or {}return{}: ".format(
            clr.HIGHLIGHT, clr.RESET, clr.HIGHLIGHT, clr.RESET
        ))
        if user_input == "where" or user_input == "w":
            where_key = input("Search for: {}".format(clr.HIGHLIGHT))
            print(clr.RESET)
            if where_key in unique_values:
                where_paths = []
                for value_path_pair in value_path_pairs:
                    try:
                        where_paths.append(value_path_pair[where_key])
                    except:
                        continue
                where_paths_len = len(where_paths)
                if where_paths_len >= 10:
                    if input("Print all {} entries? [y/n]: ".format(where_paths_len)) == "y":
                        for value in where_paths:
                            print(value)


        """
        all_values = []
        for path in self.target_list:
            #try?
            with open(path, 'r') as f:
                temp_data = json.load(f)
            try:
                val = temp_data[key]
                if val not in all_values:
                    all_values.append(val)
            except:
                continue
        num_values = len(all_values)

        if num_values >= 10:
            if input("Print all {} values in {}? [y/n]".format(
                num_values,
                key
            )) != 'y':
                return
        
        os.system("clear")
        for value in all_values:
            print(value)
        user_input = input("Press {}enter{} to return or {}where{} to show filename of specified value: ".format(
            clr.HIGHLIGHT, clr.RESET, clr.HIGHLIGHT, clr.RESET
        ))
        if user_input == "where" or user_input == "w":
        """