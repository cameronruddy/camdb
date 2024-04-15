import json

class make_meta:
    
    template_path = "config/metadata_template.json"

    def __init__(self, **kwargs):

        self.data = {}      # The metadata's metadata

        with open(self.template_path,'r') as f:
            self.data = json.load(f)

        for key in kwargs:
            if key in self.data:
                self.data[key] = kwargs[key]

    def update_field(self, **kwargs):
        for key in kwargs:
            if key in self.data:
                self.data[key] = kwargs[key]

    def reset_data(self):
        f = open(self.template_path)
        self.data = json.load(f)

    def writeout(self, filename):
        with open(filename + ".json", 'w') as outfile:
            json.dump(self.data, outfile, indent=5)

if __name__ == "__main__":
    session = make_meta()
    session.update_field(**{"version":"test", "fname":"test"})
    session.print()