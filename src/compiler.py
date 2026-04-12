import re

from src.text_to_ascii import T2A
from src.tokeniser import Tokeniser


class Compiler:
    def __init__(self, config):
        self.config = config

        self.t2a = T2A(
            "resources/fonts/", self.config["font"]["ascii"], [20, 30, 40, 50]
        )

    def __header_html(self, page):
        return """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <title>{title}</title>
                    <meta charset="UTF-16">
                    <link rel="stylesheet" href="/css/main.css">
                    <link rel="icon" type="icon/x-icon" href="[{icon}]">

                    <style>
                        @font-face {{
                            font-family: '{family}';
                            src: url('/fonts/{regular}') format('truetype');
                            font-weight: normal;
                            font-style: normal;
                        }}

                        @font-face {{
                            font-family: '{family}';
                            src: url('/fonts/{bold}') format('truetype');
                            font-weight: bold;
                            font-style: normal;
                        }}
                    </style>
                </head>

                <body style="width: {width};margin:auto">
        """.format(
            title=page["frontmatter"]["title"],
            width=page["frontmatter"]["width"],
            icon=page["frontmatter"]["icon"].lstrip(),
            family=self.config["font"]["family"],
            regular=self.config["font"]["regular"],
            bold=self.config["font"]["bold"],
        )

    def __footer_html(self, page, time_stamp):
        return """<footer>
            <hr>
            <div>
                <p>
                    Back to [[index]]
                </p>
                <br>
                <p>
                    Created with:
                    [[https://github.com/Gladon4/simple_pages|[{icon}] Simple Pages]] - {time_stamp}
                </p>
            </div>
            <script src='/js/search.js'></script>
        </footer>
        </body>""".format(
            icon="{github-white}",
            time_stamp=time_stamp,
        )

    def __get_classes_and_styles(self, p_args):
        classes = ""
        styles = ""
        type_args = []

        for arg in p_args:
            if len(arg) == 1:
                classes += arg[0] + " "
                continue

            match arg[0]:
                case "type_args":
                    type_args = arg[1:]
                case "vspace":
                    styles += "--" + arg[0] + ":" + arg[1] + " "
                    classes += "vspace "
                case _:
                    styles += arg[0] + ":" + arg[1] + ";"

        return classes, styles, type_args

    def __get_arg_values(self, args, arg_name):
        for arg in args:
            if arg[0] == arg_name:
                return arg[1:] if len(arg) > 1 else None

        return None

    def __ascii_html(self, paragraph, ascii_font):
        # TODO: fading as parameter
        size = self.__get_arg_values(paragraph["args"], "type_args")
        if size is not None:
            size = int(size[0])
        else:
            size = 0

        if paragraph["text"].startswith("#"):
            indent = 2
            new_size = 40

            if paragraph["text"].startswith("######"):
                indent = 7
                new_size = 15
            elif paragraph["text"].startswith("#####"):
                indent = 6
                new_size = 20
            elif paragraph["text"].startswith("####"):
                indent = 5
                new_size = 25
            elif paragraph["text"].startswith("###"):
                indent = 4
                new_size = 30
            elif paragraph["text"].startswith("##"):
                indent = 3
                new_size = 35

            size = size if size != 0 else new_size

            ascii_art = self.t2a.string_to_ascii(
                paragraph["text"][indent:],
                size,
                ascii_font,
                0.9,
            )
            return ascii_art

        else:
            assert size != 0, "Size has to be non zero if not a heading"

            ascii_art = self.t2a.string_to_ascii(
                paragraph["text"],
                size,
                ascii_font,
                0.9,
            )
            return ascii_art

    def __paragraph_html(self, paragraph):
        text = paragraph["text"]

        def replace_heading(match):
            heading_num = len(match.group(1))
            heading_text = match.group(2)

            return f"<h{heading_num}>{heading_text}</h{heading_num}>"

        def replace_bold(match):
            var = match.group(1)
            return f"<strong>{var}</strong>"

        def replace_italic(match):
            var = match.group(1)
            return f"<i>{var}</i>"

        def replace_italic_bold(match):
            var = match.group(1)
            return f"<i><strong>{var}</strong></i>"

        text = re.sub(r"(#{1,6})\s+([^\n]*)", replace_heading, text)

        text = re.sub(r"(?<!\*)\*\*([^*\n]+?)\*\*(?!\*)", replace_bold, text)
        text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", replace_italic, text)
        text = re.sub(r"(?<!\*)\*\*\*([^*\n]+?)\*\*\*(?!\*)", replace_italic_bold, text)

        text = text.replace("  \n", "<br>")
        text = text.replace("---", "<hr>")
        text = text.replace("___", "<hr>")

        return "<p>" + text + "</p>"

    def __columns_html(self, paragraph, col_widths):
        columns = paragraph["text"].split("@")

        if len(columns) != len(col_widths) + 1:
            print(
                "WARNING: Not the correct number of columns, skipping column paragraph!"
            )
            return ""

        columns = columns[1:]
        content = ""

        for column in columns:
            args, column = Tokeniser.get_args(column)
            p = {"text": column}
            elem = self.__paragraph_html(p)
            classes_str, styles_str, type_args = self.__get_classes_and_styles(args)

            content += f"<div class='col_container {classes_str}' style='{styles_str}'>{elem}</div>\n"

        return f"<div style='grid-template-columns: {' '.join(col + 'fr' for col in col_widths)};' class='col_wrapper'>{content}</div>"

    def __table_html(self, paragraph):
        header = ""
        body = ""
        lines = paragraph["text"].split("\n")

        make_header = self.__get_arg_values(paragraph["args"], "type_args")
        if make_header is None or make_header[0] == "":
            make_header = True
        else:
            make_header = make_header[0].lower() == "true"

        line = 0

        if make_header:
            header += "<tr>"
            header_names = lines[line].split("|")
            for name in header_names:
                if len(name) == 0:
                    continue
                header += f"<th>{name.strip()}</th>"
            header += "</tr>"
            line += 1

        while line < len(lines) and lines[line] != "":
            body += "<tr>"
            row = lines[line].split("|")
            for name in row:
                if len(name) == 0:
                    continue
                body += f"<td>{name.strip()}</td>"
            body += "</tr>"
            line += 1

        table = f"<table>{header}{body}</table>"

        return table

    def __search_bar_html(self, paragraph):
        scope = self.__get_arg_values(paragraph["args"], "type_args")
        if scope is None:
            scope = "/"
        else:
            scope = scope[0].strip()

        return f"""<div class="search-container" data-scope="{scope}">
                    <input type="text" id="searchInput" placeholder="Search pages..." />
                    <ul id="results"></ul>
                  </div>"""

    def __make_html(self, paragraph, ascii_font):
        classes_str, styles_str, type_args = self.__get_classes_and_styles(
            paragraph["args"]
        )

        # TODO: codeblock?
        match paragraph["type"]:
            case "paragraph":
                return f"<div class='{classes_str}'><div style='{styles_str}'>{self.__paragraph_html(paragraph)}</div></div>"
            case "ASCII":
                return f"<div class='ascii {classes_str}'><div style='{styles_str}'>{self.__ascii_html(paragraph, ascii_font)}</div></div>"
            case "columns":
                return f"<div class='{classes_str}'><div style='{styles_str}'>{self.__columns_html(paragraph, type_args)}</div></div>"
            case "table":
                return f"<div class='{classes_str}'><div style='{styles_str}'>{self.__table_html(paragraph)}</div></div>"
            case "raw":
                return paragraph["text"]
            case "search":
                return f"<div class='{classes_str}'><div style='{styles_str}'>{self.__search_bar_html(paragraph)}</div></div>"

            case _:
                return paragraph["text"]

    def compile(self, page, time_stamp):
        html_str = ""
        html_str += self.__header_html(page)

        for paragraph in page["paragraphs"]:
            html_str += self.__make_html(paragraph, page["frontmatter"]["ascii-font"])

        html_str += self.__footer_html(page, time_stamp)

        return html_str
