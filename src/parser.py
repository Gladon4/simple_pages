import os
import sys
import glob
import time
import re

from text_to_ascii import T2A


class Parser:
    def __init__(self, directory: str, t2a: T2A):
        self.directory = directory
        self.pages = {}
        self.t2a = t2a

    def parse(self):
        for file in self.files:
            self.__parse(file)

    def setup(self):
        self.files = glob.glob(f"{self.directory}/**/*.md", recursive=True)
        self.files = [
            "/".join(f.split("/")[len(self.directory.split("/")) :])[:-3]
            for f in self.files
        ]
        self.__make_links()
        self.__find_icons()

        assert "main" in self.files, "Main Page (main.md) must be supplied!"

    def __make_links(self):
        self.links = {}
        for file in self.files:
            self.links[file] = file
            name = file.split("/")[-1]
            if name not in self.links.keys():
                self.links[name] = file

    def __find_icons(self):
        base_icons = os.listdir("resources/icons/")
        new_icons = []

        if os.path.isdir(f"{self.directory}/icons/"):
            new_icons = os.listdir(f"{self.directory}/icons/")

        self.icons = {}
        for icon in base_icons + new_icons:
            self.icons[icon.split(".")[0]] = icon

    def __replace_links(self, line):
        def replace_internal_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]
            url = self.links.get(var, "#")
            text = name if name else var  # Use name if it exists; otherwise, use var
            return f"<a href='{url}.html'>{text}</a>"

        def replace_external_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]
            text = name if name else var  # Use name if it exists; otherwise, use var
            return f"<a href='{var}'>{text}</a>"

        def replace_icons(match):
            name = match.group(1)
            icon = self.icons.get(name, "#")
            return f"<img src=/icons/{icon} class='icon'></img>"

        line = re.sub(r"\[\{(.+?)\}\]", replace_icons, line)
        line = re.sub(
            r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_internal_link, line
        )
        line = re.sub(
            r"\[\(([^\|\]]+)(?:\|([^\]]+))?\)\]", replace_external_link, line
        )

        return line

    def __parse(self, file_name: str):
        assert file_name in self.files, f"Parser._parse: File {file_name} not found"

        self.pages[file_name] = {"elements": []}
        self.pages[file_name]["front_matter"] = {
            "title": "Placeholder",
            "width": "85%",
        }

        full_file_path = os.path.join(self.directory, file_name + ".md")
        file = open(full_file_path, "r")

        line = file.readline().rstrip()
        if line.startswith("---"):
            line = file.readline()
            while not line.startswith("---"):
                prop = line.split(":")
                self.pages[file_name]["front_matter"][prop[0]] = prop[1].rstrip()
                line = file.readline().rstrip()

        while file.tell() < os.path.getsize(full_file_path):
            line = file.readline().rstrip()

            if "/--" in line:
                line = line[: line.find("/--")]

            if line.startswith("/*"):
                while "*/" not in line:
                    line = file.readline().rstrip()

                line = line[(line.find("*/") + 2) :]

            anotations = []
            anotation_variables = []
            element = ""
            classes = []
            styles = []
            while line.startswith("@"):
                anotation = line.split(" ")
                anotations.append(anotation[0])
                if len(anotation) > 1:
                    anotation_variables.append(anotation[1:])
                else:
                    anotation_variables.append([0])
                line = file.readline().rstrip()

            element_filled = False
            for i in range(len(anotations)):
                if anotations[i] == "@ASCII":
                    element_filled = True
                    element = self.__ascii_annotaion(
                        line, int(anotation_variables[i][0])
                    )
                    classes.append("ascii")

                if anotations[i] == "@v_space":
                    element_filled = True
                    for j in range(int(anotation_variables[i][0])):
                        element += "<br>"

                if anotations[i] == "@width":
                    styles.append(f"width:{str(anotation_variables[i][0])}")

                if anotations[i] == "@txt_small":
                    classes.append("txt_small")
                elif anotations[i] == "@txt_big":
                    classes.append("txt_big")

                if anotations[i] == "@center":
                    classes.append("center")
                elif anotations[i] == "@left":
                    classes.append("left")
                elif anotations[i] == "@right":
                    classes.append("right")

                if anotations[i] == "@txt_center":
                    classes.append("txt_center")
                elif anotations[i] == "@txt_left":
                    classes.append("txt_left")
                elif anotations[i] == "@txt_right":
                    classes.append("txt_right")

            line = self.__replace_links(line)

            if not element_filled:
                # if line.startswith("___") or line.startswith("---"):
                #     element = "<hr>"
                # else:
                new_elem = self.__paragraph(line, file)
                new_elem = self.__heading(new_elem)
                new_elem = self.__ruler(new_elem)
                new_elem = self.__replace_links(new_elem)
                element = new_elem

            classes_str = ""
            styles_str = ""
            for c in classes:
                classes_str += c + " "
            for s in styles:
                styles_str += s + ";"

            self.pages[file_name]["elements"].append(
                f"<div class='{classes_str}'><div style='{styles_str}'><p>{element}</p></div></div>"
            )

        file.close()
        return

    def __ruler(self, line):
        return re.sub(r"---", r"<hr>", line)

    def __paragraph(self, line, file):
        text = ""
        while line != "":
            if "/--" in line:
                line = line[: line.find("/--")]
            text += line + "\n"
            line = file.readline().rstrip()
        return text

    def __heading(self, line):
        def replace_heading(match):
            heading_num = len(match.group(1))
            heading_text = match.group(2)

            return f"<h{heading_num}>{heading_text}</h{heading_num}>"

        return re.sub(r"(#{1,6})\s+([^\n]*)", replace_heading, line)

    def __ascii_annotaion(self, line, size=0):
        if line.startswith("#"):
            indent = 2
            new_size = 40

            if line.startswith("######"):
                indent = 7
                new_size = 15
            elif line.startswith("#####"):
                indent = 6
                new_size = 20
            elif line.startswith("####"):
                indent = 5
                new_size = 25
            elif line.startswith("###"):
                indent = 4
                new_size = 30
            elif line.startswith("##"):
                indent = 3
                new_size = 35

            size = size if size != 0 else new_size

            ascii_art = self.t2a.string_to_ascii(line[indent:], size, 0.9)
            return ascii_art

        else:
            assert size != 0, "Size has to be non zero if not a heading"

            ascii_art = self.t2a.string_to_ascii(line, size, 0.9)
            return ascii_art
