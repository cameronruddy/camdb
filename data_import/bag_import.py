import rosbag
from data_import.belt import belt
from data_import import make_img
import color_scheme as clr


class bag_import(belt):
    
    def __init__(self, config_path, bag_path, out_root, verbose, framestep):
        belt.__init__(self, config_path, bag_path, out_root, verbose)
        self.imager = make_img.make_img()
        self.frame_step = framestep     #TODO Will implement later

    def open_bag(self, bagpath):
        return rosbag.Bag(bagpath, 'r')
    
    def close_bag(self, bagfile):
        try:
            bagfile.close()
        except:
            print("Could not close {}".format(bagfile))

    def get_starttime(self, bagfile):
        try:
            return bagfile.get_start_time()
        except:
            print("{}Error{}: Could not get timestamp from {}{}{}".format(
                clr.ERROR, clr.RESET,
                clr.HIGHLIGHT, bagfile, clr.RESET))
            return None
        
    def create_images(self, bagfile):
        camera_topics = []
        sources = {}
        frame_idx = 1
        
        for cam_name in self.config["cameras"]:
            topic = self.config["cameras"][cam_name]["topic"]
            camera_topics.append(topic)
            sources[topic] = cam_name

        for topic, msg, t in bagfile.read_messages(camera_topics):
            if not (frame_idx % self.frame_step):
                good_img = False
                cam_id = sources[topic]
                this_path = self.labels[cam_id].get_whole_path()

                #TODO: Is there a better way to do this??
                if "compressed" in topic:
                    if self.imager.decompress(
                        msg,
                        this_path
                    ): good_img = True

                else:
                    if self.imager.from_raw(
                        msg,
                        this_path
                    ): good_img = True
                        
                if good_img and self.verbose:
                    print("{}Wrote image{} {} {}to{} {}.png".format(
                        clr.SUCCESS, clr.RESET,
                        self.labels[cam_id].file_idx,
                        clr.SUCCESS, clr.RESET,
                        this_path
                    ))
                
                if good_img:
                    self.meta_tools[cam_id].update_field(**{
                    "fname":(self.labels[cam_id].filename + ".png"),
                    "timestamp": t.to_sec(),
                    "source": cam_id,
                    "collection": belt.time_string(self, t.to_sec())
                    })
                    self.meta_tools[cam_id].writeout(this_path)

                    if self.verbose:
                        print("{}Wrote JSON{} {} {}to{} {}.json".format(
                            clr.SUCCESS, clr.RESET,
                            self.labels[cam_id].file_idx,
                            clr.SUCCESS, clr.RESET,
                            this_path
                        ))
                
                    self.out_paths.append(this_path + '.png')
                    self.out_paths.append(this_path + '.json')
                    
                else:
                    if self.verbose:
                        print("{}Failed to write{} {}".format(
                            clr.ERROR, clr.RESET,
                            this_path
                        ))

                self.labels[cam_id].file_idx += 1
            frame_idx += 1

    def run_belt(self):

        for bagpath in self.item_paths:
            bagfile = self.open_bag(bagpath)
            belt.parse_dirname(self, bagpath, bagfile)
            self.create_images(bagfile)