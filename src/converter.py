from text_to_ascii import T2A
from parser import Parser

import os
import shutil
import time
import datetime


class Converter:
    def __init__(self):
        pass

    def setup(self, input_directory, output_directory, page_font, ascii_font):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.page_font = page_font
        self.ascii_font = ascii_font

        self.t2a = T2A(f"resources/fonts/{ascii_font}", [20, 30, 40, 50])
        self.parser = Parser(input_directory, self.t2a)

    def convert(self):
        time_stamp = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
        verison_time_stamp = int((time.time() * 1000) % 1000000)

        shutil.rmtree(self.output_directory)
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(f"{self.output_directory}/fonts", exist_ok=True)
        shutil.copy(
            f"resources/fonts/{self.page_font}",
            f"{self.output_directory}/fonts/{self.page_font}",
        )
        shutil.copytree(
            "resources/css",
            f"{self.output_directory}/css/{verison_time_stamp}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/icons", f"{self.output_directory}/icons/", dirs_exist_ok=True
        )
        shutil.copytree(
            "resources/img", f"{self.output_directory}/img/", dirs_exist_ok=True
        )

        if os.path.isdir(f"{self.input_directory}/icons"):
            shutil.copytree(
                f"{self.input_directory}/icons",
                f"{self.output_directory}/icons",
                dirs_exist_ok=True,
            )

        if os.path.isdir(f"{self.input_directory}/img"):
            shutil.copytree(
                f"{self.input_directory}/img",
                f"{self.output_directory}/img",
                dirs_exist_ok=True,
            )

        self.parser.setup()
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
                            <head>
                                <title>{title}</title>
                                <link rel="stylesheet" href="/css/{time_stamp}/main.css">
                            </head>
                            <body style="width: {width};margin:auto">
                    """.format(
                        title=front_matter["title"],
                        width=front_matter["width"],
                        time_stamp=verison_time_stamp,
                    )
                )

                for element in self.parser.pages[page]["elements"]:
                    f.write(element)

                f.write(
                    """
                    <footer>
                        <hr>
                        <div>
                            <a href='/main.html'>Frontpage</a>
                            <br>
                            <p>
                                Page version from: {time_stamp}
                                <br>
                                Created with:
                                <a href='https://github.com/Gladon4/ascii_page_creator'>
                                <img src='/icons/github-white.png' class='icon'></img>
                                Simple Pages
                                </a>
                            </p>
                        </div>
                    </footer>
                    """.format(
                        time_stamp=time_stamp,
                    )
                )
                f.write("</body>")
