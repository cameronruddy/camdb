# Stevens Camera Database
A suite of tools for generating and modifying large directories of images and associated metadata files. These tools were developed to automate large scale tasks such as recovering images from archive files and editing metadata en masse.

Many of these commands can be run on individual files or on whole directories. In the case of the ladder, all files beneath the provided directory will be operated on. Otherwise, just the file passed will be edited.

## Commands

`python3 main.py [-a --camera_angles] [-b --bagimport] [-c --config] [-d --decimate_copy] [-D --decimate_reduce] [-f --framestep] [-g --gps] [-m --metadata] [-n --renumber] [-o --outdir] [-p --copy] [-r --removepii] [-v --verbose] [-V --video]`

`-a` `[CSV_FILE]` `[TARGET_DIR]` Appends camera angles to metadata files in the targeted directory. Requires 2 arguments, the CSV file containing camera poses and the target directory.

`-b` Imports data from `.bag` files, a type of archive file used commonly in the Robot Operating System (ROS). `-b` must typically be run with `-c`, `-o`, and more optionally `-f`.

`-c` Specifies a configuration file for any data import. While most imports *can* run with the default config, it is highly recommend to enter a custom config file in the `./config` directory. While the `-c` flag can accept a file from anywhere in the file system, keeping them in the `./config` directory can help reduce confusion.

`-d` Decimates files in the targeted directory by a provided amount. Rather than deleting the files from the target directory, this function will make a new directory (set with `-o`) and copy the non-decimated files over there. E.g., for a decimation factor of 5, 1 in every 5 images will be copied over to the new directory. 

`-D` Similar to `-d`, but removes the files from the target directory instead of copying them over to a new directory. E.g., for a decimation factor of 5, 1 in every 5 files will ***not*** be deleted from the target.

`-f` Sets the number of frames to jump before saving the next image. Since many of the import functions are recovering images from video (`-b` and `-V`), there will often be 30+ frames per second. Use this to reduce the overall memory demand. E.g., a framestep of 15 will skip 15 frames before saving the next image.

`-g` `[GPS_FILE]`, `[TARGET_DIR]` Appends gps data to metadata files, like how `-a` appends camera angles to metadata. 

`-m` Opens a command-line editor for metadata files. There are several commands that can be used with this tool. The 5 primary commands are `edit`, `summary`, `undo`, `write`, and `exit`.
- `edit` is invoked by entering a field's name. The field will become highlighted and a new value can be entered.
- `summary` or `s` will provide a list of all entries for a specific field. From this page, you can enter `where` or `w` to receive a list of all the files that have a specific value. Further, after `where`, if you wish to delete all the files that have been identified, you can enter `DELETE`.
- `undo` or `u` will undo the last `edit` command
- `write` or `w` will save all changes made by `edit` so far. If the user attempts to exit before writing, they will be prompted to write.
- `exit` or `e` will exit the program.

`-n` Renumbers files within their respective directories to range from 0-*n*. Especially useful after deleting files.

`-o` Set the output directory. If this is not invoked, a custom directory name with a timestamp will be created in the present working directory, and results will be written there.

`-p` Copy images from one place to another and generate metadata files.

`-v` Add extra status messages.

`-V` Import data from .mp4 files. Similar to `-b`, this command works best with the `-c`, `-o`, and `-f` flags defined.
