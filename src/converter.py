from text_to_ascii import T2A
from parser import Parser

import os
import shutil
import time
import datetime


class Converter:
    def __init__(self):
        pass

    def setup(self, input_directory, output_directory, default_page_font, default_ascii_font):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.default_page_font = default_page_font
        self.default_ascii_font = default_ascii_font

        self.t2a = T2A("resources/fonts/", f"{default_ascii_font}", [20, 30, 40, 50])
        self.parser = Parser(input_directory, self.t2a)

    def convert(self):
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
        verison_time_stamp = int((time.time() * 1000) % 1000000)

        shutil.rmtree(self.output_directory)
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(f"{self.output_directory}/fonts", exist_ok=True)
        shutil.copy(
            f"resources/fonts/{self.default_page_font}",
            f"{self.output_directory}/fonts/{self.default_page_font}",
        )
        shutil.copytree(
            "resources/css",
            f"{self.output_directory}/css/{verison_time_stamp}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/icon", f"{self.output_directory}/icon/{verison_time_stamp}", dirs_exist_ok=True
        )
        shutil.copytree(
            "resources/img", f"{self.output_directory}/img/{verison_time_stamp}", dirs_exist_ok=True
        )
        shutil.copy("resources/.htaccess",  f"{self.output_directory}/.htaccess")

        if os.path.isdir(f"{self.input_directory}/icon/"):
            shutil.copytree(
                f"{self.input_directory}/icon",
                f"{self.output_directory}/icon/{verison_time_stamp}",
                dirs_exist_ok=True,
            )

        if os.path.isdir(f"{self.input_directory}/img"):
            shutil.copytree(
                f"{self.input_directory}/img",
                f"{self.output_directory}/img/{verison_time_stamp}",
                dirs_exist_ok=True,
            )

        self.parser.setup(verison_time_stamp)
        self.parser.parse()

        for page in self.parser.pages:
            front_matter = self.parser.pages[page]["front_matter"]

            if "/" in page:
                os.makedirs(
                    os.path.join(self.output_directory, os.path.dirname(page)),
                    exist_ok=True,
                )

            with open(f"{self.output_directory}/{page}.html", "w") as f:
                f.write(
                    """<!DOCTYPE html>
                            <html lang="en">
                            <head>
                                <title>{title}</title>
                                <meta charset="UTF-16">
                                <link rel="stylesheet" href="/css/{time_stamp}/main.css">
                                <link rel="icon" type="icon/x-icon" href="/icon/{time_stamp}/{icon}.png">
                            </head>
                            <body style="width: {width};margin:auto">
                    """.format(
                        title=front_matter["title"],
                        width=front_matter["width"],
                        time_stamp=verison_time_stamp,
                        icon=front_matter["icon"]
                    )
                )

                for element in self.parser.pages[page]["elements"]:
                    f.write(element)

                f.write(
                    """
                    <footer>
                        <hr>
                        <div>
                            <p>
                                Back to <a href='/'>{front_page}</a>
                            </p>
                            <br>
                            <p>
                                Created with:
                                <a href='https://github.com/Gladon4/simple_pages'>
                                <img src='/icon/{verison_time_stamp}/github-white.png' class='icon'></img>
                                Simple Pages</a> - {time_stamp}
                            </p>
                        </div>
                    </footer>
                    """.format(
                        time_stamp=time_stamp,
                        verison_time_stamp=verison_time_stamp,
                        front_page=self.parser.pages["index"]["front_matter"]["title"]
                    )
                )
                f.write("</body>")
