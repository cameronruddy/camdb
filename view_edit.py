from colorama import Fore, Back
import json, os
import color_scheme as clr
import pdb

##########################################################
# Sort of an all-purpose tool for handling metadata files
# Currently supports editing fields and summarizing fields
# Will recurse though a given directory and target all json files
##########################################################

##### COLOR CODES #####

EDIT = [Fore.BLACK, Back.CYAN, Fore.LIGHTCYAN_EX]
CHANGED = [Fore.LIGHTCYAN_EX, Back.RESET, Fore.LIGHTCYAN_EX]
FLOAT = [Fore.LIGHTCYAN_EX, Back.RESET, Fore.LIGHTBLUE_EX]
STRING = [Fore.LIGHTCYAN_EX, Back.RESET, Fore.LIGHTMAGENTA_EX]
BOOL = [Fore.LIGHTCYAN_EX, Back.RESET, Fore.LIGHTCYAN_EX]
NULL = [Fore.LIGHTCYAN_EX, Back.RESET, Fore.LIGHTGREEN_EX]
ORIG = [Fore.RESET, Back.RESET, Fore.RESET]
RESET = [Fore.RESET, Back.RESET, Fore.RESET]

class view_edit:

    def __init__(self, target_list, verbose, *args):
        # Parse target_list based on if it's a single value or a list
        try:
            with open(target_list, 'r') as f:
                self.target_list = [line[:-1] for line in f]
        except TypeError:
            self.target_list = target_list

        try:
            first_path = self.target_list[0]
        except TypeError:
            first_path = self.target_list
        
        with open(first_path, 'r') as f:
            self.data = json.load(f)

        if args:
            self.title = args[0]
        else:
            self.title = ""

        self.verbose = verbose
        self.color_data = {}
        for key in self.data.keys():
            try:
                self.color_data[key] = {sub_key:ORIG for sub_key in self.data[key].keys()}
            except AttributeError:
                self.color_data[key] = ORIG

        self.changed_values = {}
        self.undo_buffer = {}

    def print_keys(self):
        os.system("clear")
        print("Current values in {}:\n".format(
            self.title
        ))

        for key in self.data.keys():
            try:
                sub_keys = self.data[key].keys()
                print("\t{}:".format(
                    key
                ))

                for sub_key in sub_keys:
                    color_handle = self.color_data[key][sub_key]
                    print("\t\t{}{}{}{}{}: {}{}{}".format(
                        color_handle[0],
                        color_handle[1],
                        sub_key,
                        RESET[0],
                        RESET[1],
                        color_handle[2],
                        self.data[key][sub_key],
                        RESET[0]
                    ))
            except TypeError:
                continue

            except AttributeError:
                color_handle = self.color_data[key]
                print("\t{}{}{}{}{}: {}{}{}".format(
                   color_handle[0], 
                    color_handle[1],
                    key,
                    RESET[0],
                    RESET[1],
                    color_handle[2],
                    self.data[key],
                    RESET[0]
                ))
    
    def get_subkey(self, dict, target_key):
        for parent_key in dict.keys():
            try:
                for sub_key in dict[parent_key].keys():
                    if target_key in sub_key:
                        return True, dict[parent_key][target_key]
            except AttributeError:
                continue
        return False, None

    # This passes the dictionary in but I'm not sure if it will always use the *actual* passed dictionary (like a pointer)
    # Or if it will make a copy and then use that
    def write_subkey(self, dict, target_key, value):
        for parent_key in dict.keys():
            try:
                for sub_keys in dict[parent_key].keys():
                    if target_key in sub_keys:
                        dict[parent_key][target_key] = value
                        return True
            except AttributeError:
                continue
        return False


    def check_type(self, string):
        # Function to manually set the type of the passed argument
        if string == "":
            return ["", STRING]

        string = string.split() # See if input is actually a list
        if len(string) == 1:
            string = string[0]  # String is not a list, see if it matches any of the following
            if string == "true" or string == "True":
                return [True, BOOL]
            elif string == "false" or string == "False":
                return [False, BOOL]
            elif string == "null" or string == "None":
                return [None, NULL]
            try:
                return [float(string), FLOAT]   # Maybe it's a number?
            except ValueError:
                pass    # Not a number :(

            return [string, STRING]
        else:   # It was actually a list all along
            return [string, STRING]

    def update_data(self, key, value):
        user_input = input("\nModify {}\"{}\"{} from {}\"{}\"{} to: {}".format(
            Fore.LIGHTCYAN_EX, key, Fore.RESET,
            Fore.LIGHTCYAN_EX, value, Fore.RESET,
            Fore.LIGHTCYAN_EX
        ))
        print(Fore.RESET)
        return self.check_type(user_input)

    def summary(self, key):
        # See if key is even valid, or if it's a valid subkey
        if key not in self.data:
            if not self.get_subkey(self.data, key):
                return
        
        value_path_pairs = []
        for path in self.target_list:
            with open(path, 'r') as f:
                temp_data = json.load(f)
            try:
                # See if value is a sub key
                sub_exists, sub_value = self.get_subkey(temp_data, key)
                if sub_exists:
                    value_path_pairs.append({sub_value:path})
                # If not, see if it's a main key
                else:
                    value_path_pairs.append({temp_data[key]:path})
            except AttributeError:
                continue
            except KeyError:
                continue
                # Not in dict, keep going

        unique_values = []
        for val_path_pair in value_path_pairs:
            temp = next(iter(val_path_pair))
            if temp not in unique_values:
                unique_values.append(temp)

        num_unique_values = len(unique_values)
        if num_unique_values >= 10:
            if input("Print all {} values in {}? [y/n] ".format(
                num_unique_values,
                key
            )) != 'y':
                return

        user_input = ""
        while (user_input != "return") and (user_input != "r"):
            os.system("clear")
            for value in unique_values:
                print(value)

            user_input = input("Enter {}where{} to show filename(s) of specified value or {}return{}: ".format(
            clr.HIGHLIGHT, clr.RESET, clr.HIGHLIGHT, clr.RESET
            ))
            if user_input == "where" or user_input == "w":
                where_key, color = self.check_type(input("Search for: {}".format(clr.HIGHLIGHT)))
                print(clr.RESET)
                if where_key in unique_values:
                    where_paths = []
                    for value_path_pair in value_path_pairs:
                        try:
                            where_paths.append(value_path_pair[where_key])
                        except:
                            continue
                    where_paths.sort()
                    where_paths_len = len(where_paths)
                    if where_paths_len <= 10 or input("Print all {} entries? [y/n]: ".format(where_paths_len)) == "y":
                        for value in where_paths:
                            print(value)
                        maybe_delete = input("\nEnter DELETE to delete all targeted files, or press enter to return {}".format(clr.ERROR))
                        print(clr.RESET)
                        if maybe_delete == "DELETE":
                            if input("{}Are you absolutely sure you want to delete {}{}{} files?{} [y/n] ".format(
                                clr.ERROR, clr.HIGHLIGHT, where_paths_len, clr.ERROR, clr.RESET )) == "y":
                                for file in where_paths:
                                    with open(file, 'r') as f:
                                        temp_data = json.load(f)
                                        try:
                                            img_file = temp_data["fname"]
                                            os.remove(os.path.join(os.path.dirname(file), img_file))
                                        except:
                                            continue
                                    os.remove(file)
                                    self.target_list.remove(file)
                                return

    def edit_entry(self, key):
        if key in self.color_data.keys():
            self.color_data[key] = EDIT
            self.print_keys()
            value, color_code = self.update_data(key, self.data[key])
            self.undo_buffer = {key:self.data[key]}
            self.data[key] = value
            self.changed_values[key] = value
            self.color_data[key] = color_code
            self.print_keys()

        else:
            for parent_key in self.data.keys():
                try:
                    if key in self.data[parent_key].keys():
                        self.color_data[parent_key][key] = EDIT
                        self.print_keys()
                        value, color_code = self.update_data(
                            key, 
                            self.data[parent_key][key])
                        self.data[parent_key][key] = value
                        try:
                            self.changed_values[parent_key][key] = value
                        except KeyError:
                            self.changed_values[parent_key] = {key: value}
                        self.color_data[parent_key][key] = color_code
                        self.print_keys()
                except AttributeError:
                    continue

    def writeout(self):
        ## Exit if nothing has been changed
        if self.changed_values == {}:
            return
        
        ## Exit if user quits
        if input("Write to {} files? [y/n] ".format(
            len(self.target_list)
        )) != 'y':
            return

        # Iterate though all files
        for target in self.target_list:
            # Load data for this file
            with open(target, 'r') as f:
                temp_data = json.load(f)
            # Update data
            for key in self.changed_values.keys():
                try:
                    sub_keys = self.changed_values[key].keys()
                    for sub_key in sub_keys:
                        temp_data[key][sub_key] = self.changed_values[key][sub_key]
                except:
                    temp_data[key] = self.changed_values[key]
            # Writeout
            with open(target, 'w') as f:
                json.dump(temp_data, f, indent=5)
                if self.verbose:
                    print("{}Writing{} to {}".format(
                        clr.SUCCESS, clr.RESET,
                        target
                    ))
        # Reset changed values
        self.changed_values = {}
    
    def undo(self):
        for key in self.undo_buffer.keys():
            stash = {key:self.data[key]}
            self.data[key] = self.undo_buffer[key]
            self.changed_values[key] = self.undo_buffer[key]
        self.undo_buffer = stash

    def main_loop(self):
        user_input = ""
        while user_input != "exit" and user_input != "e":
            self.print_keys()
            user_input = input("\nSpecify field to edit, summary, undo, write, or {}exit{}: ".format(
                Fore.LIGHTRED_EX, Fore.RESET
            ))
            current_keys = self.data.keys()
            if user_input == "summary" or user_input == "s":
                temp = input("Specify a field to summarize: {}".format(
                    clr.HIGHLIGHT
                ))
                print(clr.RESET)
                self.summary(temp)
            elif user_input == "write" or user_input == "w":
                self.writeout()
            elif user_input == "undo" or user_input == "u":
                self.undo()
            else:
                self.edit_entry(user_input)
        #return self.changed_values
        if self.changed_values != {}:
            if input("{}Warning{}: Unsaved changed, writeout before quitting? [y/n] ".format(
                clr.WARNING, clr.RESET
            )) == "y":
                self.writeout()
        
        return

if __name__ == "__main__":
    
    with open("./config/metadata_template.json", 'r') as f:
        data = json.load(f)

    session = view_edit(data)
    session.main_loop()

    
        



