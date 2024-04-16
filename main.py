import argparse
import os, sys, json

import dir_crawler
import view_edit
import color_scheme as clr
import ioparse as io
from data_import import bag_import, copy_import, mp42img
from misc_tools import pii_remover, renumber_files, csv2meta, data_pruner

import pdb

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

#TODO
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
                    nargs=2,
                    metavar=("[PATH]", "[DECIMATION_FACTOR]"),
                    help="Reduce the number of images in a dataset, deletes from provided dir",
                    action="store"
                    )

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
if args.bagimport:
    print("Starting import from bagfile...")
    config_file = io.handle_config(args.config)
    if args.framestep == None:
        args.framestep = 1

    targets, target_dirs = io.parse_input(args.bagimport, ".bag")

    reader = bag_import.bag_import(config_file, 
                               targets, 
                               str(io.parse_output(args.outdir)),
                               args.verbose,
                               int(args.framestep))
    reader.run_belt()

# Copy from existing data
elif args.copy:
    print("Starting copy import...")
    config_file = io.handle_config(args.config)
    text, ext = os.path.splitext(args.copy)
    if ext == '':
        ext = input("Please specify image type to copy: ")

    copier = copy_import.copy_import(config_file,
                                    str(io.parse_input(args.copy, ext)),
                                    str(io.parse_output(args.outdir)),
                                    args.verbose,
                                    
    )
    copier.run_belt()
    
# Import from mp4 files
elif args.video:
    print("Starting MP4 import...")
    config_file = io.handle_config(args.config)
    #start_datetime = input("Please provide start datetime [YYYY-MM-DD HH:MM:SS]: ")
    if args.framestep:
        framestep = args.framestep
    else:
        framestep = 1

    # GoPro MP4s have extension in all caps for some reason
    # Try that and if there's nothing try lower case extension
    target_files, target_dirs = io.parse_input(args.video, ".MP4")
    if target_files == []:
        target_files, target_dirs = io.parse_input(args.video, ".mp4")

    reader = mp42img.mp42img(config_file,
                             target_files,
                             str(io.parse_output(args.outdir)),
                             args.verbose,
                             None,      # TODO: have this point to a path or user input
                             framestep
    )
    reader.run_belt()


##### Metadata Modify #####
## And other fun tools ##

if args.metadata:
    paths = dir_crawler.dir_crawler(
        args.metadata,
        ".json",
        None
    )
    targets = paths.traverse()
    session = view_edit.view_edit(
        targets,
        args.verbose,
        args.metadata
    )
    session.main_loop()

## Decimate Copy ##
if args.decimate_copy or args.decimate_remove:
    try:
        data_path, decimation_factor = args.decimate_copy
    except TypeError:
        data_path, decimation_factor = args.decimate_remove
    
    session = dir_crawler.dir_crawler(data_path,
                                      "all",
                                      None
                                    )
    session.traverse()
    data_dirs = session.get_dirs()
    if args.decimate_copy:
        base_dir = io.parse_output(args.outdir)
    else:
        base_dir = None
    run_idx = 0
    for this_dir in data_dirs:
        if args.verbose:
            print("{}Decimating{} {}...".format(
                clr.HIGHLIGHT, clr.RESET, this_dir))
        
        if args.decimate_copy:
            data_pruner.decimate_multiple_filetypes(
                this_dir, decimation_factor, os.path.join(base_dir, str(run_idx)))
        elif args.decimate_remove:
            data_pruner.decimate_multiple_filetypes(
                this_dir, decimation_factor, None
            )
        run_idx += 1
        if args.verbose:
            print("{}Decimated{} {} by a factor of {}".format(
                clr.SUCCESS, clr.RESET, this_dir, decimation_factor
            ))

if args.removepii:
    # TODO: make this more idiot (me) proof
    # TODO: how to make this run without sudo
    
    rmpii = pii_remover.pii_remover(args.removepii)
    rmpii.iterate(args.outdir)

if args.gps:
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


if args.camera_angles:
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
    session = renumber_files.renumber_files(io.parse_input(
        args.renumber,".json"))
    session.renumber()