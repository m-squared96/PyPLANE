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

    def get_system_names(self):
        return list(self.SOE_params.keys())

    def get_system(self, sys_name):
        return self.SOE_params[sys_name]

    def __iter__(self):
        return GalleryIterator(self)


class GalleryIterator:
    def __init__(self, gallery):
        self.gallery = gallery
        self.index = 0
        self.gallery_items = gallery.get_system_names()
        self.gallery_len = len(self.gallery_items)

    def __next__(self):
        if self.index > self.gallery_len - 1:
            raise StopIteration
        sys_name = self.gallery_items[self.index]
        self.index += 1
        return self.gallery.get_system(sys_name)


if __name__ == "__main__":
    g = Gallery("resources/gallery_2D.json", 2)
    print(g)
