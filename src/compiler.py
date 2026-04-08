from src.text_to_ascii import T2A


class Compiler:
    def __init__(self, config):
        self.config = config

        self.t2a = T2A(
            "resources/fonts/", self.config["font"]["ascii"], [20, 30, 40, 50]
        )

    def __header_html(self, page, version_time_stamp):
        return """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <title>{title}</title>
                    <meta charset="UTF-16">
                    <link rel="stylesheet" href="/css/{version_time_stamp}/main.css">
                    <link rel="icon" type="icon/x-icon" href="/icon/{version_time_stamp}/{icon}">

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
            version_time_stamp=version_time_stamp,
            icon=page["frontmatter"]["icon"],
            family=self.config["font"]["family"],
            regular=self.config["font"]["regular"],
            bold=self.config["font"]["bold"],
        )

    def __footer_html(self, page, time_stamp, version_time_stamp):
        return """
        <footer>
            <hr>
            <div>
                <p>
                    Back to [[index]]
                </p>
                <br>
                <p>
                    Created with:
                    <a href='https://github.com/Gladon4/simple_pages'>
                    <img src='/icon/{verison_time_stamp}/github-white.webp' class='icon'></img>
                    Simple Pages</a> - {time_stamp}
                </p>
            </div>
            <script src='/js/{verison_time_stamp}/search.js'></script>
        </footer>
        </body>
        """.format(time_stamp=time_stamp, verison_time_stamp=version_time_stamp)

    def __get_classes_and_styles(self, p_args):
        classes = ""
        styles = ""
        type_args = []

        for arg in p_args:
            if len(arg) == 1:
                classes += arg[0] + " "

            elif arg[0] != "type_args":
                styles += arg[0] + ":" + arg[1] + " "

            else:
                type_args = arg[1:]

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

    def __make_html(self, paragraph, ascii_font):
        classes_str, styles_str, type_args = self.__get_classes_and_styles(
            paragraph["args"]
        )

        match paragraph["type"]:
            case "paragraph":
                return f"<div class='{classes_str}'><div style='{styles_str}'>{paragraph['text']}</div></div>"

            case "ASCII":
                return f"<div class='ascii {classes_str}'><div style='{styles_str}'>{self.__ascii_html(paragraph, ascii_font)}</div></div>"
            case _:
                return ""

    def compile(self, page, time_stamp, version_time_stamp):
        html_str = ""
        html_str += self.__header_html(page, version_time_stamp)

        for paragraph in page["paragraphs"]:
            html_str += self.__make_html(paragraph, page["frontmatter"]["ascii-font"])

        html_str += self.__footer_html(page, time_stamp, version_time_stamp)

        return html_str
