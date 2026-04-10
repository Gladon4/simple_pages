from typing_extensions import Optional


class Linker:
    def __init__(self, config, all_files):
        self.config = config
        self.all_files = all_files
        self.pages: Optional[list[dict]] = None

        self.links = self.__link_map(self.all_files)

    def __link_map(self, files):
        links = {}

        for file in files:
            links[file] = file

            path_withot_ext = file.split(".")[0]
            if path_withot_ext not in links.keys():
                links[path_withot_ext] = file

            name_with_ext = file.split("/")[-1]
            if name_with_ext not in links.keys():
                links[name_with_ext] = file

            name_without_ext = file.split("/")[-1].split(".")[0]
            if name_without_ext not in links.keys():
                links[name_without_ext] = file

        return links

    def link(self, html_page):
        return html_page
