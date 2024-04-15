import json, os
import pdb

class renumber_files:
    
    def __init__(self, path):

        with open(path, 'r') as f:
            self.path_list = [line[:-1] for line in f]


    def renumber(self):
        last_dir = ""

        for meta_file in self.path_list:
            current_dir = os.path.dirname(meta_file)
            
            if current_dir != last_dir:
                file_idx = 1

            last_dir = current_dir

            stripped_current_fname, toss = os.path.splitext(meta_file)
            base_fname = meta_file[:-13]
            out_base = "{}{:08d}".format(base_fname, file_idx)
            file_idx += 1

            if os.path.isfile(stripped_current_fname + ".png"):
                img_name = out_base + ".png"
                if not os.path.isfile(img_name):
                    os.rename(stripped_current_fname + ".png", img_name)

            elif os.path.isfile(stripped_current_fname + ".jpeg"):
                img_name = out_base + ".jpeg"
                if not os.path.isfile(img_name):
                    os.rename(stripped_current_fname + ".jpeg", img_name)
            
            else:                
                continue

            ### Rename fname field inside existing metadata field
            with open(meta_file, 'r') as f:
                temp_data = json.load(f)
            
            temp_data["fname"] = os.path.basename(img_name)

            with open(meta_file, 'w') as f:
                json.dump(temp_data, f, indent=5)

            meta_name = out_base + ".json"
            os.rename(stripped_current_fname + ".json", meta_name)
            
    def old_method(self):
        for file in self.path_list:
            text,ext = os.path.splitext(file)
            if ext == ".json":
                with open(file, 'r') as f:
                    temp_data = json.load(f)

                temp_text = os.path.basename(text)
                fname = ("{}{:08d}{}".format(
                temp_text[:-8], meta_idx, ".jpg"
                ))
                temp_data["fname"] = fname
                out_file = ("{}{:08d}{}".format(
                text[:-8], meta_idx, ".json"
                ))
                with open(file, 'w') as f:
                    json.dump(temp_data, f, indent=5)
                meta_idx += 1

            else:
                out_file = ("{}{:08d}{}".format(
                text[:-8], img_idx, ext
                ))
                img_idx += 1
            
            os.rename(file, out_file)

if __name__ == "__main__":

    import dir_crawler as dc

    path = "./default_out"


    files = dc.dir_crawler(path,
                           os.getcwd() + "/config",
                           "targets.txt",
                           ".json",
                           verbose=False)

    files.traverse()
    files.reorganize()
    files.writeout()



    session = renumber_files("config/targets.txt")
    session.renumber()
