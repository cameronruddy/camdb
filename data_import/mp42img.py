### Simple tool for extracting images from MP4 files

import os, sys, json, csv
import cv2
import numpy as np
from misc_tools import time_handler as th
from data_import import make_label, make_meta
from data_import.belt import belt
import color_scheme as clr

class mp42img(belt):
    
    def __init__(self, config_path, mp4_paths, out_root, verbose, start_datetimes, framestep):
        belt.__init__(self, config_path, mp4_paths, out_root, verbose)
        self.start_datetime=start_datetimes
        self.framestep = int(framestep)
        self.camera_idx = "camA012" #TODO: fix this
        self.video_and_starttime = self.package_starttime_and_video(self.item_paths, start_datetimes)

    def package_starttime_and_video(self, video_vec, time_vec):
        video_and_starttime = []
        try:
            if os.path.isfile(time_vec):
                pass
                # TODO: read from config? From file?
            else:
                raise TypeError # To fall into except routine
        except TypeError:
            # Ask for user input
            for video_file in video_vec:
                timestamp = input("Enter start time for {} [YYYY-MM-DD HH:MM:SS] ".format(
                os.path.basename(video_file)
                ))
                # Format into unix timestamp for ease of use
                timestamp = float(th.utc2epoch(timestamp))
                video_and_starttime.append([video_file, timestamp])
        return video_and_starttime


    def parse_dirname(self, timestamp):
        # This one only needs timestamp since runs are divided by file, not directory
        self.labels[self.camera_idx].file_idx = 1
        self.labels[self.camera_idx].set_test_time(timestamp)
        if not os.path.exists(self.labels[self.camera_idx].abspath):
            os.makedirs(self.labels[self.camera_idx].abspath)


    def generate_frames(self, video_file, basetime):
        # Open the video file
        cap = cv2.VideoCapture(video_file)
        total_num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        num_steps = int(total_num_frames/self.framestep)
        frame_vec = np.linspace(0, total_num_frames, num=num_steps)
        num_frames = 1
        for step in frame_vec:
            cap.set(cv2.CAP_PROP_POS_FRAMES, step)
            time_diff = (step)/fps # total difference from time_base
            success, frame = cap.read()
            if success:
                this_path = self.labels[self.camera_idx].get_whole_path()
                imgpath = this_path + ".png"
                try:
                    cv2.imwrite(imgpath, frame)
                    if self.verbose:
                        print("{}Wrote{} image {} to file {}".format(
                            clr.SUCCESS, clr.RESET, self.labels[self.camera_idx].file_idx, imgpath
                        ))
                except:
                    if self.verbose:
                        print("{}Error{}: cannot write image {} to file {}{}".format(
                            clr.ERROR, clr.RESET, frame, imgpath
                        ))
                    continue
                try:
                    self.meta_tools[self.camera_idx].update_field(**{
                        "fname":(self.labels[self.camera_idx].filename + ".png"),
                        "timestamp": basetime + time_diff,
                        "source": self.camera_idx,
                        "collection": belt.time_string(self, basetime + time_diff)
                    })
                    self.meta_tools[self.camera_idx].writeout(this_path)
                    if self.verbose:
                        print("{}Wrote{} JSON {} to file {}".format(
                            clr.SUCCESS, clr.RESET, self.labels[self.camera_idx].file_idx, this_path + ".json"
                        ))
                except:
                    if self.verbose:
                        print("{}Error{}: cannot write image {} to file {}".format(
                            clr.ERROR, clr.RESET, self.labels[self.camera_idx].file_idx, this_path + ".json"
                        ))
                self.labels[self.camera_idx].file_idx += 1
            num_frames += 1

    def run_belt(self):
        for video_file, this_timestamp in self.video_and_starttime:
            self.parse_dirname(this_timestamp)
            self.generate_frames(video_file, this_timestamp)

if __name__ == "__main__":
    video_file = "/media/storage/wriva_raw/deliverable3/2024-03-15/100GOPRO/GX010011.MP4"
