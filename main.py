import argparse
import os, sys, json

import dir_crawler
import view_edit
import color_scheme as clr
from data_import import bag_import, copy_import, mp42img
from misc_tools import pii_remover, renumber_files, csv2meta, data_pruner

import pdb

DEFAULT_OUT = "./default_out"

def handle_import(path, config, ext):
    # Try to get root directory from import first
    # Else, see if there is a default path in the config file
    # If there is no valid path, exit program
    
    try:
        if os.path.isdir(path):
            targets = dir_crawler.dir_crawler(path,
                                            os.getcwd() + "/config",
                                            "targets.txt",
                                            ext, 
                                            False)
            targets.traverse()
            targets.reorganize()
            targets.writeout()
            return "config/targets.txt"
            
        elif os.path.isfile(path):
            with open("config/targets.txt", 'w') as f:
                f.write(path + '\n')
            return "config/targets.txt"


        else: 
            print("{}Error{}: {}{}{} is not a file or directory".format(
                clr.ERROR, clr.RESET,
                clr.HIGHLIGHT, path, clr.RESET))
            sys.exit(1)

    except TypeError:
        try:
            with open(config, 'r') as f:
                temp = json.load(f)
                dpath = temp["in_default"]
                if os.path.isdir(dpath):
                    targets = dir_crawler.dir_crawler(dpath,
                                                    os.getcwd() + "/config",
                                                    "targets.txt",
                                                    ext,
                                                    False)
                else:
                    print("{}Error{}: directory identified as {}{}{} does not exist".format(
                        clr.ERROR, clr.RESET,
                        clr.HIGHLIGHT, dpath, clr.RESET
                    ))
                    sys.exit(1)

        except:
            print("{}Error{}: cannot import data. Import path found in {}{}{} as {}{}{} is not valid".format(
                clr.ERROR, clr.RESET,
                clr.HIGHLIGHT, config, clr.RESET,
                clr.HIGHLIGHT, dpath, clr.RESET
            ))
            sys.exit(1)
    
    except:
        sys.exit(1)

    targets.traverse()
    targets.reorganize()
    targets.writeout()
    return "config/targets.txt"

def format_output(outdir):
    # Checks to see if directories are already made and then returns path
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outdir

def handle_output(outdir, configfile):
    # Similar to handle import
    # If outdir is specified with -o, use that
    # Otherwise, look for a outdir in config
    # If no path, ask to make outdir

    if outdir != None:
        ## Chop off a / at the end
        # For formatting into downstream functions

        if outdir[-1] == '/':
            outdir = outdir[:-1]

        # Check if valid
        if os.path.isdir(outdir):
            print("Using output directory \"{}{}{}\"".format(
                clr.SUCCESS, outdir, clr.RESET
            ))
            return outdir

        # Not valid! Ask to make dirs
        else:
            print("{}Warning{}: \"{}{}{}\" was specified for output but no such directory exists".format(
                clr.WARNING, clr.RESET, 
                clr.HIGHLIGHT, outdir, clr.RESET
            ))
            if input("Create {}{}{} and continue? [y/n]: ".format(
                clr.HIGHLIGHT, outdir, clr.RESET)) == 'y':
                return format_output(outdir)
    
    elif configfile != None:
        try:
            with open(configfile, 'r') as f:
                temp = json.load(f)
                outdir = temp["label"]["out_default"]

            if os.path.isdir(outdir):
                print("Found default output path {}{}{} in config file {}{}{}".format(
                    clr.HIGHLIGHT, outdir, clr.RESET,
                    clr.HIGHLIGHT, configfile, clr.RESET
                ))
                if input("Continue with these settings? [y/n]: ") == 'y':
                    return format_output(outdir)
                
        except KeyError as e:
            print("{}Warning{}: No output directory found in {}{}{}".format(
                clr.WARNING, clr.RESET,
                clr.HIGHLIGHT, configfile, clr.RESET
            ))
    
    else:
        print("{}Warning{}: No output directory or config file was specified".format(clr.WARNING, clr.RESET))

    if input("Continue import with default path {}{}{}? [y/n]: ".format(
        clr.HIGHLIGHT, DEFAULT_OUT, clr.RESET
    )) == 'y':
        return format_output(DEFAULT_OUT)
    else:
        sys.exit(0)

def handle_config(configpath):
    # If a config file is specified, use that
    # Otherwise, use the default

    if configpath != None:
        if os.path.isfile(configpath):
            print("Using {}{}{} as configuration file".format(
                clr.SUCCESS, configpath, clr.RESET
            ))
            return configpath
        else:
            print("{}Warning{}: Provided metadata file {}{}{} is not a file".format(
            clr.WARNING, clr.RESET,
            clr.HIGHLIGHT, configpath, clr.RESET
            ))
    
    print("{}Warning{}: No configuration file provided".format(clr.WARNING, clr.RESET))
    if input("Continue using default configuration file? [y/n]: ") == "y":
        return "config/default.json"
    else:
        sys.exit(0)
    
    

parser = argparse.ArgumentParser(
    prog="CamDB",
    description="Software for managing a CamDB database"
)
parser.add_argument('-a',
                    '--camera_angles',
                    nargs=2,
                    metavar=("[CSV_FILE]", "[TARGET_DIR]"),
                    help="Add camera angle data from csv file to existing metadata files",
                    )


parser.add_argument('-b',
                    '--bagimport',
                    help="Import data from bagfiles, provide path to root dir",
                    metavar="",
                    action="store"
                    )

parser.add_argument('-c',
                    '--config',
                    help="Specify a configuration file to be used. If none is specified, config/default.json is used",
                    metavar="",
                    action='store'
                    )

parser.add_argument('-d',
                    '--decimate_copy',
                    nargs=2,
                    metavar=("[PATH]", "[DECIMATION_FACTOR]"),
                    help="Reduce the number of images in a dataset, makes copy. If decimation factor is a fraction, pass as list [num, den]",
                    action="store"
                    )

#TODO
parser.add_argument('-D',
                    "--decimate_remove",
                    help="Reduce the number of images in a dataset, deletes from provided dir")

parser.add_argument('-f',
                    '--framestep',
                    metavar='',
                    help="Skip this many images before next save")

parser.add_argument('-g',
                    '--gps',
                    nargs =2,
                    metavar=('[GPS_FILE]', '[TARGET_DIR]'),
                    help="Add gps data from csv file to existing metadata files")

parser.add_argument('-m',
                    '--metadata',
                    help="Modify contents of metadata file(s)",
                    metavar="",
                    action="store")

parser.add_argument("-n",
                    "--renumber",
                    help="Renumbers images and json files in a directory from 1 -> max",
                    metavar="",
                    action="store")

parser.add_argument('-o',
                    '--outdir',
                    help="Specify output path",
                    metavar="",
                    action="store"
                    )

parser.add_argument('-p',
                    '--copy',
                    help="Import data by copying from existing dir",
                    metavar="",
                    action="store"
                    )

parser.add_argument('-r',
                    '--removepii',
                    help="Remove PII from all sub-directories in provided directory",
                    metavar="",
                    action='store'
                    )


parser.add_argument('-v',
                    '--verbose',
                    help="enable extra messages",
                    action='store_true')

parser.add_argument("-V",
                    "--video",
                    help="Import from mp4 file",
                    metavar="",
                    action="store")

args = parser.parse_args()

##### Data Import Modules #####

# Import from bag file
if args.bagimport != None:
    print("Starting import from bagfile...")
    config_file = handle_config(args.config)
    if args.framestep == None:
        args.framestep = 1

    reader = bag_import.bag_import(config_file, 
                               str(handle_import(args.bagimport, config_file, ".bag")), 
                               str(handle_output(args.outdir, config_file)),
                               args.verbose,
                               int(args.framestep))
    reader.run_belt()

# Copy from existing data
elif args.copy != None:
    print("Starting copy import...")
    config_file = handle_config(args.config)
    text, ext = os.path.splitext(args.copy)
    if ext == '':
        ext = input("Please specify image type to copy: ")

    copier = copy_import.copy_import(config_file,
                                    str(handle_import(args.copy, config_file, ext)),
                                    str(handle_output(args.outdir, config_file)),
                                    args.verbose,
                                    
    )
    copier.run_belt()
    
# Import from mp4 files
if args.video:
    print("Starting MP4 import...")
    config_file = handle_config(args.config)
    #start_datetime = input("Please provide start datetime [YYYY-MM-DD HH:MM:SS]: ")
    if not args.framestep:
        framestep = 1
    else:
        framestep = args.framestep

    reader = mp42img.mp42img(config_file,
                             str(handle_import(args.video, config_file, ".MP4")),
                             str(handle_output(args.outdir, config_file)),
                             args.verbose,
                             None,      # TODO: have this point to a path or user input
                             framestep
    )
    reader.run_belt()


##### Metadata Modify #####
    #TODO: Make all of this more idiot proof


if args.metadata != None:
    paths = dir_crawler.dir_crawler(
        args.metadata,
        os.getcwd() + "/config",
        "targets.txt",
        ".json",
        False
    )
    paths.traverse()
    paths.reorganize()
    paths.writeout()
    session = view_edit.view_edit(
        "./config/targets.txt",
        args.verbose,
        args.metadata
    )
    session.main_loop()

## Decimate ##
if args.decimate:
    data_path, decimation_factor = args.decimate
    session = dir_crawler.dir_crawler(data_path,
                                      None,
                                      None,
                                      "all",
                                      False,

    )
    session.traverse()
    session.reorganize()
    data_dirs = session.get_dirs()
    base_dir = handle_output(args.outdir, None)
    run_idx = 0
    for this_dir in data_dirs:
        if args.verbose:
            print("{}Decimating{} {}...".format(clr.HIGHLIGHT, clr.RESET, this_dir))
        data_pruner.copy_decimate_multiple_filetypes(this_dir, decimation_factor, os.path.join(base_dir, str(run_idx)))
        run_idx += 1
        if args.verbose:
            print("{}Decimated{} {} by a factor of {}".format(
                clr.SUCCESS, clr.RESET, this_dir, decimation_factor
            ))

if args.removepii != None:
    # TODO: make this more idiot (me) proof
    
    rmpii = pii_remover.pii_remover(args.removepii)
    rmpii.iterate(args.outdir)

if args.gps != None:
    infile, outpath = args.gps
    session = csv2meta.csv2meta(args.verbose)
    session.import_data(infile, ["Measurement_DateTime",
                                 "GPS_lat",
                                 "GPS_lon",
                                 "GPS_alt"])
    session.add2meta(outpath,
                        ["Measurement_DateTime", "timestamp"],
                        **{"extrinsics":{
                            "lat":"GPS_lat",
                            "lon":"GPS_lon",
                            "alt":"GPS_alt"
                        }})
    del session


if args.camera_angles != None:
    infile, outpath = args.camera_angles
    session = csv2meta.csv2meta(args.verbose)
    session.import_data(infile, ["timestamp",
                                 "omega",
                                 "phi",
                                 "kappa"])
    session.add2meta(outpath,
                     ["timestamp", "timestamp"],
                     **{"extrinsics":{
                        "omega":"omega",
                        "phi":"phi",
                        "kappa":"kappa"
                     }})
    
if args.renumber:
    session = renumber_files.renumber_files(handle_import(args.renumber, None, ".json"))
    session.renumber()