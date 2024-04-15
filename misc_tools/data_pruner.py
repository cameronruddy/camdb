### Collection of tools used to reduce the number of files in a dataset

import os,sys,json
import shutil
#from rename_files import rename_files as rf
import color_scheme as clr
import pdb

def configure(input):
    if type(input) == list:
        target = input
    else:
        target = [input]
    return target

## Reduce number of files by a constant factor
# Removes targeted files from system
# Decimation factor can be a scalar (e.g., for factor of n, keep 1 of every n samples)
# Or a fraction (e.g., for a factor of n/m, keep m of every n samples)
# To use a fractional decimation factor, pass list of [numerator, denominator]
def decimate(data_path, decimation_factor):
    # Setup params
    paths = configure(data_path)
    if type(decimation_factor) == list:
        num = int(decimation_factor[0])
        den = int(decimation_factor[1])
    else:
        num = int(decimation_factor)
        den = 1
        
    for target_dir in paths:
        target_files = [os.path.abspath(f) for f in os.listdir(target_dir)]
        # Actual Decimation Loop
        idx = 1
        for file in target_files:
            if idx > den:
                os.remove(os.path.abspath(file))
            if idx >= num:
                idx = 1
                continue
            idx += 1

## Reduce number of files by a constant factor
# Instead of removing files, makes a copy of "nondiscarded" files
# Decimation factor can be a scalar (e.g., for factor of n, keep 1 of every n samples)
# Or a fraction (e.g., for a factor of n/m, keep m of every n samples)
# To use a fractional decimation factor, pass list of [numerator, denominator]
# Only pass one directory at a time
def copy_decimate(data_files, decimation_factor, outdir):
    # Setup params
    target_files = configure(data_files)
    if type(decimation_factor) == list:
        num = int(decimation_factor[0])
        den = int(decimation_factor[1])
    else:
        num = int(decimation_factor)
        den = 1
    
    # Make sure that path exists
    path_base = os.path.abspath(outdir)
    if not os.path.isdir(path_base):
        os.makedirs(path_base)

    # Actual Decimation Loop
    idx = 1
    total_files = len(target_files)
    num_deleted = 0
    for file in target_files:
        if idx <= den:
            filename = os.path.basename(file)
            shutil.copyfile(file, os.path.join(path_base, filename))
        else:
            num_deleted += 1
        if idx >= num:
            idx = 1
            continue
        idx += 1
    return num_deleted, total_files

## Use this method to decimate multiple filetypes by the same factor
def decimate_multiple_filetypes(all_files, decimation_factor):
    configure(all_files)
    extensions = []
    for file in all_files:
        text, ext = os.path.splitext(file)
        if ext not in extensions: extensions.append(ext)
    for this_ext in extensions:
        file_list = []
        for f in os.listdir(all_files):
            if f.endswith(this_ext):
                file_list.append(os.path.abspath(f))
        decimate(file_list, decimation_factor)

def copy_decimate_multiple_filetypes(all_files, decimation_factor, outfile):
    target_dirs = configure(all_files)
    extensions = []
    for this_dir in target_dirs:
        for file in os.listdir(this_dir):
            text, ext = os.path.splitext(file)
            if ext not in extensions: extensions.append(ext)
    for this_ext in extensions:
        for this_dir in target_dirs:
            file_list = []
            target_files = os.listdir(this_dir)
            target_files.sort()
            for f in target_files:
                if f.endswith(this_ext):
                    file_list.append(os.path.join(this_dir, f))
            copy_decimate(file_list, decimation_factor, outfile)
    



if __name__ == "__main__":
    data_path = "/media/storage/wriva_deliverables/240325-siteRTX0002-delivery/siteRTX0002-SIT-campus/camA012-GoPro-UGV-1/2024-03-15-12-29-27"
    copy_decimate_multiple_filetypes(data_path, 2, "/media/storage/wriva_deliverables/copy_test")