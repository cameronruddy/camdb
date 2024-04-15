import os,sys
import color_scheme as clr
from datetime import datetime
from dir_crawler import dir_crawler as dc

DEFAULT_OUT = "./default_out"
TIME_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"

def novel_dirname(root_dir):
    ### Make a novel directory name ###
    idx = 0
    while idx < 10:
        this_dir = "{}/{}".format(root_dir, 
            (lambda dt : dt.strftime(TIME_FORMAT))(datetime.now()))
        if not os.path.isdir(this_dir):
            return this_dir
        else:
            idx += 1

def parse_input(path, extension, *args):
    ### Parse Input Path ###
    # Returns list of paths to files and list of file dirs
    # If input is a valid file, returns list of length 1
    # If input is a directory, returns all files of specified type recursively
    # If input is list, basically a passthrough
    # Args can be used to provide custom error messages

    if os.path.isdir(path):
        session = dc(path, extension, None)
        targets = session.traverse()
        target_dirs = session.get_dirs()
    elif os.path.isfile(path):
        targets = [path]
        target_dirs = [os.path.dirname(path)]

    return targets, target_dirs


def parse_output(outdir, *args):
    ### Handle output dir name ###
    if outdir:
        # Chop off any extra "/" at the end
        if outdir[-1] == "/":
            outdir = outdir[:-1]
        
        # Check if dir is valid
        if os.path.isdir(outdir):
            clr.print_warning("\"{}{}{}\" was specified for output but no such directory exists".format(
                clr.HIGHLIGHT, outdir, clr.RESET
            ))
            if input("Create {}{}{} and continue? [y/n]: ".format(
                clr.HIGHLIGHT, outdir, clr.RESET
            )) == "y":
                return outdir
    else:
        clr.print_warning("No output directory was specified")
        new_dir = novel_dirname(os.getcwd())
        if input("Continue with generated path {}{}{}? [y/n] ".format(
            clr.HIGHLIGHT, new_dir, clr.RESET
        )) == "y":
            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)
            return new_dir
        else:
            sys.exit(0)

def handle_config(configpath):
    ### Get config file ### 
    if configpath:
        if os.path.isfile(configpath):
            clr.print_success("Using {}{}{} as configuration file".format(
                clr.SUCCESS, configpath, clr.RESET
            ))
            return configpath
        else:
            clr.print_warning("Provided metadata file {}{}{} is not a valid file".format(
                clr.HIGHLIGHT, configpath, clr.RESET
            ))
    clr.print_warning("No configuration file provided")
    if input("Continue using default configuration file? [y/n]: ") == "y":
        return "config/default.json"
    else:
        sys.exit(0)
        
