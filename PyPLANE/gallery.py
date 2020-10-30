import json


class Gallery:
    def __init__(self, gallery_file_name, num_dims):
        self.num_dims = num_dims

        with open(gallery_file_name, "r") as f:
            gallery_dict = json.load(f)

        gallery_list = gallery_dict["gallery"]
        self.SOE_params = {sys["system_name"]: sys for sys in gallery_list}

    def __str__(self):
        gallery_str = json.dumps(self.SOE_params, sort_keys=True, indent=4)
        return gallery_str


if __name__ == "__main__":
    g = Gallery("resources/gallery_2D.json", 2)
    print(g)
