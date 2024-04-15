import json, pprint, os, sys
import color_scheme as clr
import dir_crawler
import view_edit


class meta_modify:

    def __init__(self, verbose):
        self.verbose = verbose

    def load_meta(self, filename):
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def writeout(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=5)
            if self.verbose:
                print("{}Writing{} to {}".format(
                    clr.SUCCESS, clr.RESET,
                    filename
                ))
    
    def add_keys(self, filename, **kwargs):
        self.load_meta(filename)
        for key in kwargs:
            try:
                sub_keys = kwargs[key].keys()
                for sub_key in sub_keys:
                    self.data[key][sub_key] = kwargs[key][sub_key]

            except:
                self.data[key] = kwargs[key]
        self.writeout(filename)

    def delete_keys(self, filename, **kwargs):
        self.load_meta(filename)
        for key in kwargs:
            del self.data[key]
        self.writeout(filename)

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


    ##### This has been replaced by the view_edit.py module #####
    
    def view_edit(self, target):
        if os.path.isfile(target):
            filename = target

        elif os.path.isdir(target):
            session = dir_crawler.dir_crawler(
                target,
                os.getcwd(),
                "config/targets.txt",
                ".json",
                False
            )
            session.traverse()
            session.reorganize()
            session.writeout()
            with open(os.getcwd() + "/config/targets.txt", 'r') as f:
                file_list = [line[:-1] for line in f]
            
            try:
                filename = file_list[0]
            except IndexError:
                print("{}Error{}: No metadata files found in {}{}{}".format(
                    clr.ERROR, clr.RESET,
                    clr.HIGHLIGHT, target, clr.RESET
                ))
                sys.exit(1)

        if filename == "":
            print("{}Error{}: {}{}{} is not a valid filename".format(
                clr.ERROR, clr.CLEAR,
                clr.HIGHLIGHT, filename, clr.CLEAR
            ))
            sys.exit(1)

        self.load_meta(filename)
        user_input = ""
        changed_values = {}
        targeted_files = [filename]
        
        while(user_input != "exit"):
            os.system("clear")
            print("Current metadata from {}:".format(filename))
            pprint.pprint(self.data)
            current_keys = self.data.keys()
            user_input = input("\nSpecify field to edit or {}\"exit\"{} to finish: ".format(
                clr.HIGHLIGHT, clr.RESET
            ))
            if user_input in current_keys:
                try: # See if there are sub directories
                    sub_keys = self.data[user_input].keys()
                    os.system("clear")
                    pprint.pprint(self.data[user_input])
                    sub_user_input = input("\nSpecify field to edit: ")
                    if sub_user_input in sub_keys:
                        sub_new_value = input(
                            "Modify {}\"{}\"{} from {}\"{}\"{} to: {}".format(
                                clr.HIGHLIGHT, sub_user_input, clr.RESET,
                                clr.HIGHLIGHT, self.data[user_input][sub_user_input], clr.RESET,
                                clr.HIGHLIGHT
                            )
                        )
                        print(clr.RESET)
                        corrected_value = self.check_type(sub_new_value)
                        self.data[user_input][sub_user_input] = corrected_value
                        try:
                            changed_values[user_input][sub_user_input] = corrected_value
                        except KeyError:
                            changed_values[user_input] = {sub_user_input: corrected_value}

                except:
                    new_value = input("Modify {}\"{}\"{} from {}\"{}\"{} to: {}".format(
                            clr.HIGHLIGHT, user_input, clr.RESET,
                            clr.HIGHLIGHT, self.data[user_input], clr.RESET,
                            clr.HIGHLIGHT
                        ))
                    print(clr.RESET)

                
                    corrected_value = self.check_type(new_value)
                    self.data[user_input] = corrected_value
                    changed_values[user_input] = corrected_value
        
        if changed_values != {}:
            
            if os.path.isfile(target):
                if input("Apply changes to all files in {}{}{}? [y/n]: ".format(
                    os.path.dirname(target))) == 'y':
                    
                    target_path = os.path.dirname(filename)
                    all_files = os.listdir(target_path)
                    for file in all_files:
                        text,ext = os.path.splitext(file)
                        if ext == ".json":
                            targeted_files.append("{}/{}".format(
                                target_path,
                                file
                            ))

            elif os.path.isdir(target):
                if input("Apply changes to all files in {}{}{}? [y/n]: ".format(
                    clr.HIGHLIGHT, target, clr.RESET
                )) == 'y':
                    targeted_files = file_list
                else:
                    targeted_files = filename

        for file in targeted_files:
            self.add_keys(file, **changed_values)


    def view_edit_exp(self, target):
        if os.path.isfile(target):
            filename = target

        elif os.path.isdir(target):
            session = dir_crawler.dir_crawler(
                target,
                os.getcwd(),
                "config/targets.txt",
                ".json",
                False
            )
            session.traverse()
            session.reorganize()
            session.writeout()
            with open(os.getcwd() + "/config/targets.txt", 'r') as f:
                file_list = [line[:-1] for line in f]
            
            try:
                filename = file_list[0]
            except IndexError:
                print("{}Error{}: No metadata files found in {}{}{}".format(
                    clr.ERROR, clr.RESET,
                    clr.HIGHLIGHT, target, clr.RESET
                ))
                sys.exit(1)

        if filename == "":
            print("{}Error{}: {}{}{} is not a valid filename".format(
                clr.ERROR, clr.CLEAR,
                clr.HIGHLIGHT, filename, clr.CLEAR
            ))
            sys.exit(1)

        self.load_meta(filename)
        session = view_edit.view_edit(self.data, filename)
        changed_values = session.main_loop()

        if changed_values != {}:
            
            if os.path.isfile(target):
                if input("Apply changes to all files in {}{}{}? [y/n]: ".format(
                    os.path.dirname(target))) == 'y':
                    
                    target_path = os.path.dirname(filename)
                    all_files = os.listdir(target_path)
                    for file in all_files:
                        text,ext = os.path.splitext(file)
                        if ext == ".json":
                            targeted_files.append("{}/{}".format(
                                target_path,
                                file
                            ))

            elif os.path.isdir(target):
                if input("Apply changes to all files in {}{}{}? [y/n]: ".format(
                    clr.HIGHLIGHT, target, clr.RESET
                )) == 'y':
                    targeted_files = file_list
                else:
                    targeted_files = filename

            for file in targeted_files:
                self.add_keys(file, **changed_values)
