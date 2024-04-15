import os, sys, re
import dir_crawler
import subprocess

class pii_remover:

    def __init__(self, inpath):
        session = dir_crawler.dir_crawler(
            inpath,
            "config/",
            "pii_targets.txt",
            ".json",
            False
        )

        session.traverse()
        session.reorganize()
        session.writeout()

    def get_out_dir(self, outpath, path):
        ### What the heck was I cooking here ###

        m = re.search("\d{6}-\D{5,10}\d{2,4}-\D{8}.*", path)
        this_out_dir = "{}/{}".format(outpath, m.group(0))
        if not os.path.exists(this_out_dir):
            os.makedirs(this_out_dir)

        return this_out_dir

    def iterate(self, outpath):
        with open("config/pii_targets.txt", 'r') as f:
            target_paths = [line[:-1] for line in f]
        
        first_path = os.path.dirname(target_paths[0])

        dir_names = [[first_path,
                      self.get_out_dir(outpath, first_path)]]
        for target in target_paths:
            this_path = os.path.dirname(target)
            if this_path != dir_names[-1][0]:
                try:
                    dir_names.append([this_path, 
                        self.get_out_dir(outpath, this_path)])
                
                except:
                    #TODO: Maybe have some kind of error handling here?
                    print("error lol")
        
        #stash_pwd = os.getcwd()
        #os.chdir("/home/rfal/projects/wriva/extra_tools/data-annotation-tool/automatic_detection")

        for indir, outdir in dir_names:

            payload = "sudo docker run --rm -it --mount type=bind,source={},target=\"/input\",readonly -v {}:/output wriva:pii_removal".format(
                indir,outdir
            )
            
            # payload = "bash automatic_run.sh -i {} -o {}".format(
            #     indir, outdir
            # )
            os.system(payload)
            
        #os.chdir(stash_pwd)