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
        self.current_file = None

    def parse(self):
        for file in self.files:
            self.current_file = file
            self.__parse(file)

    def setup(self):
        self.files = glob.glob(f"{self.directory}/**/*.md", recursive=True)
        self.files = [
            "/".join(f.split("/")[len(self.directory.split("/")) :])[:-3]
            for f in self.files
        ]
        self.__make_links()
        self.__find_icons()
        self.__find_images()

        assert "index" in self.files, "Main Page (index.md) must be supplied!"

    def __make_links(self):
        self.links = {}
        for file in self.files:
            self.links[file] = file
            name = file.split("/")[-1]
            if name not in self.links.keys():
                self.links[name] = file

    def __find_icons(self):
        base_icons = os.listdir("resources/icon/")
        new_icons = []

        if os.path.isdir(f"{self.directory}/icon/"):
            new_icons = os.listdir(f"{self.directory}/icon/")

        self.icons = {}
        for icon in base_icons + new_icons:
            self.icons[icon.split(".")[0]] = icon

    def __find_images(self):
        base_images = os.listdir("resources/img/")
        new_images = []

        if os.path.isdir(f"{self.directory}/img/"):
            new_images = os.listdir(f"{self.directory}/img/")

        self.images = {}
        for image in base_images + new_images:
            self.images[image.split(".")[0]] = image

    def __replace_links(self, line):
        def replace_internal_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]
            url = self.links.get(var, "not_link")

            # Remove longest common prefix path, to not add the current directory again
            while url.split("/")[0] == self.current_file.split("/")[0]:
                url = "/".join(url.split("/")[1:])

            text = name if name else var  # Use name if it exists; otherwise, use var
            return f"<a href='{url}.html'>{text}</a>"

        def replace_external_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]
            text = name if name else var  # Use name if it exists; otherwise, use var
            return f"<a href='{var}'>{text}</a>"

        def replace_icons(match):
            name = match.group(1)
            icon = self.icons.get(name, "not_link")
            return f"<img src=/icon/{icon} class='icon'></img>"

        line = re.sub(r"\[\{(.+?)\}\]", replace_icons, line)
        line = re.sub(
            r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_internal_link, line
        )
        line = re.sub(
            r"\[\(([^\|\]]+)(?:\|([^\]]+))?\)\]", replace_external_link, line
        )

        return line

    def __replace_images(self, line):
        def replace_internal_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            width = match.group(2)  # Extract the optional name from [[var|name]]
            url = self.images.get(var, "not_image")
            return f"<img src=/img/{url} alt='{var}' style='width:{width};' class='img'></img>"

        def replace_external_link(match):
            url = match.group(1)  # Extract the variable name from [[var]]
            width = match.group(2)  # Extract the optional name from [[var|name]]
            return f"<img src={url} alt='{url}' style='width:{width};' class='img'></img>"

        line = re.sub(
            r"!\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_internal_link, line
        )
        line = re.sub(
            r"!\[\(([^\|\]]+)(?:\|([^\]]+))?\)\]", replace_external_link, line
        )

        return line
    
    def __replace_styling(self, line):
        def replace_bold(match):
            var = match.group(1) 
            return f"<strong>{var}</strong>"
        
        def replace_italic(match):
            var = match.group(1) 
            return f"<i>{var}</i>"

        def replace_italic_bold(match):
            var = match.group(1) 
            return f"<i><strong>{var}</strong></i>"
        
        if len(line) == 0:
            return line
        
        # Check for invisible character to not mess up ascii art
        if line[0] == "​":
            return line

        line = re.sub(
            r"(?<!\*)\*\*([^*\n]+?)\*\*(?!\*)", replace_bold, line
        )
        line = re.sub(
            r"(?<!\*)\*([^*\n]+?)\*(?!\*)", replace_italic, line
        )
        line = re.sub(
            r"(?<!\*)\*\*\*([^*\n]+?)\*\*\*(?!\*)", replace_italic_bold, line
        )


        return line

    def __get_cols(self, line, file, vars):
        line = file.readline().rstrip()
        elem = ""

        count = int(vars[0])

        for i in range(count):
            (
                anotations,
                anotation_variables,
                element,
                classes,
                styles,
                section_type,
            ) = self.__get_elem(line, file)
            line = file.readline().rstrip()

            classes_str = ""
            styles_str = ""
            for c in classes:
                classes_str += c + " "
            for s in styles:
                styles_str += s + ";"
            elem += f"<div class='col_container {classes_str}' style='{styles_str}'><p>{element}</p></div>\n"

        spacing = ""
        if len(vars) - 1 < count:
            spacing = " 1fr" * count
        else:
            for s in vars[1:]:
                spacing += f" {int(s)}fr"

        wrapper = f"<div style='grid-template-columns: {spacing};' class='col_wrapper'>{elem}</div>"

        return wrapper

    def __get_table(self, line, file, vars):
        header = ""
        body = ""

        make_header = True
        if len(vars) == 1:
            if vars[0] == "false":
                make_header = False

        if make_header:
            header += "<tr>"
            line = self.__replace_images(line)
            line = self.__replace_links(line)
            header_names = line.split("|")
            for name in header_names:
                header += f"<th>{name.strip()}</th>"
            header += "</tr>"
            line = file.readline().rstrip()
            line = file.readline().rstrip()

        while line != "":
            if "/--" in line:
                line = line[: line.find("/--")]
            if line.startswith("@"):
                line = self.__get_div(line, file)

            body += "<tr>"
            line = self.__replace_images(line)
            line = self.__replace_links(line)
            row = line.split("|")
            for name in row:
                body += f"<td>{name.strip()}</td>"
            body += "</tr>"
            line = file.readline().rstrip()

        table = f"<table>{header}{body}</table>"

        return table

    def __pull_out_headings_and_paragraphs(self, element):
        pattern = r'(<h[123456][^>]*>.*?</h[123456]>)'
        parts = re.split(pattern, element, flags=re.DOTALL)

        if len(parts) <= 1:
            return element

        result = []
        i = 0

        while i < len(parts):
            if re.match(pattern, parts[i], flags=re.DOTALL):
                result.append(parts[i])  # keep header as-is
                i += 1
                content = ""
                # collect all non-header lines until next header or end
                while i < len(parts) and not re.match(pattern, parts[i], flags=re.DOTALL):
                    content += parts[i].strip()
                    i += 1
                if content:
                    result.append(f"<p>\n{content}\n</p>")
            else:
                i += 1  # skip anything before the first header

        return "\n".join(result)

    def __get_div(self, line, file):
        (
            anotations,
            anotation_variables,
            element,
            classes,
            styles,
            section_type,
        ) = self.__get_elem(line, file)

        classes_str = ""
        styles_str = ""
        for c in classes:
            classes_str += c + " "
        for s in styles:
            styles_str += s + ";"

        if section_type == "p":
            element = self.__pull_out_headings_and_paragraphs(element)
            return f"<div class='{classes_str}'><div style='{styles_str}'>{element}</div></div>"

        elif section_type == "col":
            return f"<div class='{classes_str}'><div style='{styles_str}'>{element}</div></div>"

    def __get_elem(self, line, file):
        anotations = []
        anotation_variables = []
        element = ""
        classes = []
        styles = []
        section_type = "p"
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
            if anotations[i] == "@background":
                styles.append(f"background-color:{str(anotation_variables[i][0])}")
            if anotations[i] == "@txt_color":
                styles.append(f"color:{str(anotation_variables[i][0])}")

            if anotations[i] == "@color_inv":
                classes.append("inverted")

            if anotations[i] == "@rounded":
                classes.append("rounded")

            if anotations[i] == "@small_bar":
                classes.append("small_bar")

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

            if anotations[i] == "@columns":
                section_type = "col"
                element_filled = True
                vars = anotation_variables[i]
                element = self.__get_cols(line, file, vars)

            if anotations[i] == "@table":
                element_filled = True
                vars = anotation_variables[i]
                element = self.__get_table(line, file, vars)

        if not element_filled:
            new_elem = self.__paragraph(line, file)
            new_elem = self.__heading(new_elem)
            new_elem = self.__ruler(new_elem)
            element = new_elem

        element = self.__replace_styling(element)
        element = self.__replace_images(element)
        element = self.__replace_links(element)

        return (
            anotations,
            anotation_variables,
            element,
            classes,
            styles,
            section_type,
        )

    def __parse(self, file_name: str):
        assert file_name in self.files, f"Parser._parse: File {file_name} not found"

        self.pages[file_name] = {"elements": []}
        self.pages[file_name]["front_matter"] = {
            "title": "Placeholder",
            "width": "85%",
            "ascii-font": self.t2a.default_font,
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

            self.pages[file_name]["elements"].append(self.__get_div(line, file))

        file.close()
        return

    def __ruler(self, line):
        return re.sub(r"[-_]{3,}", r"<hr>", line)

    def __paragraph(self, line: str, file):
        text = ""
        while line != "":
            if "/--" in line:
                line = line[: line.find("/--")]
            if line.startswith("@"):
                line = self.__get_div(line, file)

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

            ascii_art = self.t2a.string_to_ascii(line[indent:], size, self.pages[self.current_file]["front_matter"]["ascii-font"], 0.9)
            return ascii_art

        else:
            assert size != 0, "Size has to be non zero if not a heading"

            ascii_art = self.t2a.string_to_ascii(line, size, self.pages[self.current_file]["front_matter"]["ascii-font"], 0.9)
            return ascii_art
