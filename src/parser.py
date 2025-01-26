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
        self.files = glob.glob(f"{directory}/**/*.md", recursive=True)
        self.files = ["/".join(f.split("/")[1:])[:-3] for f in self.files]
        self.__make_links()

        assert "main" in self.files, "Main Page (main.md) must be supplied!"
        self.__parse("main")

        while len(self.files) != 0:
            file = self.files[0]
            self.__parse(file)

    def __make_links(self):
        self.links = {}
        for file in self.files:
            self.links[file] = file
            name = file.split("/")[-1]
            if name not in self.links.keys():
                self.links[name] = file

    def __replace_links(self, line):
        def replace_var(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]
            url = self.links.get(
                var, "#"
            )  # Look up the variable in the dictionary (default to "#" if not found)
            text = name if name else var  # Use name if it exists; otherwise, use var
            return f"<a href='{url}.html'>{text}</a>"

        return re.sub(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_var, line)

    def __parse(self, file_name: str):
        assert file_name in self.files, f"Parser._parse: File {file_name} not found"

        self.files.remove(file_name)
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

            if "//" in line:
                line = line[: line.find("//")]

            if line.startswith("/*"):
                while "*/" not in line:
                    line = file.readline().rstrip()

                line = line[(line.find("*/") + 2) :]

            anotations = []
            anotation_variables = []
            element = ""
            classes = []
            while line.startswith("@"):
                anotation = line.split(" ")
                anotations.append(anotation[0])
                if len(anotation) > 1:
                    anotation_variables.append(anotation[1:])
                else:
                    anotation_variables.append([0])
                line = file.readline().rstrip()

            for i in range(len(anotations)):
                if anotations[i] == "@ASCII":
                    element = self.__ascii_annotaion(
                        line, int(anotation_variables[i][0])
                    )
                    classes.append("ascii")

                if anotations[i] == "@v_space":
                    for j in range(int(anotation_variables[i][0])):
                        element += "<br>"

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

            if element == "":
                if line.startswith("#"):
                    element = self.__heading(line)
                elif line.startswith("___") or line.startswith("---"):
                    self.pages[file_name]["elements"].append("<hr>")
                    continue
                else:
                    new_elem = self.__paragraph(line, file)
                    new_elem = self.__replace_links(new_elem)
                    element = new_elem

            classes_str = ""
            for c in classes:
                classes_str += c + " "

            self.pages[file_name]["elements"].append(
                f"<div class='{classes_str}'><p>{element}</p></div>"
            )

        file.close()
        return

    def __paragraph(self, line, file):
        text = ""
        while line != "":
            if "//" in line:
                line = line[: line.find("//")]
            text += line + " "
            line = file.readline().rstrip()
        return text

    def __heading(self, line):
        heading = 1

        if line.startswith("######"):
            heading = 6
        elif line.startswith("#####"):
            heading = 5
        elif line.startswith("####"):
            heading = 4
        elif line.startswith("###"):
            heading = 3
        elif line.startswith("##"):
            heading = 2

        return f"<h{heading}>{line[heading+1:]}</h{heading}>"

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
