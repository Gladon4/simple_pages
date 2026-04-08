import configparser
import datetime
import glob
import os
import shutil
import time

import tqdm

import src.compiler as cmp
import src.tokeniser as tok

# from src.text_to_ascii import T2A


class PageMaker:
    def __init__(self, input_dir, output_dir, redirection):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.redirection = redirection

        default_config = configparser.ConfigParser()
        custom_config = configparser.ConfigParser()
        config = configparser.ConfigParser()

        default_config.read(os.path.join(os.getcwd(), "config.ini"))
        config.read_dict(default_config)

        if os.path.isfile(os.path.join(input_dir, "config.ini")):
            custom_config.read(os.path.join(input_dir, "config.ini"))
            config.read_dict(custom_config)

        self.config = config

        self.default_page_font = config["font"]["regular"]
        self.default_bold_font = config["font"]["bold"]
        self.default_ascii_font = config["font"]["ascii"]

        # self.t2a = T2A("resources/fonts/", config["font"]["ascii"], [20, 30, 40, 50])

        self.tokeniser = tok.Tokeniser(self.config)
        self.compiler = cmp.Compiler(self.config)

        self.time_stamp = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
        self.verison_time_stamp = int((time.time() * 1000) % 1000000)

        self.files = glob.glob(f"{self.input_dir}/**/*.md", recursive=True)
        self.files = [
            "/".join(f.split("/")[len(self.input_dir.split("/")) :])[:-3]
            for f in self.files
        ]

        if "index" not in self.files:
            assert False, "index.md not present in input directory."

    def __copy_resources(self):
        shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/fonts", exist_ok=True)
        shutil.copy(
            f"resources/fonts/{self.default_page_font}",
            f"{self.output_dir}/fonts/{self.default_page_font}",
        )
        shutil.copy(
            f"resources/fonts/{self.default_bold_font}",
            f"{self.output_dir}/fonts/{self.default_bold_font}",
        )
        shutil.copytree(
            "resources/css",
            f"{self.output_dir}/css/{self.verison_time_stamp}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/icon",
            f"{self.output_dir}/icon/{self.verison_time_stamp}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/img",
            f"{self.output_dir}/img/{self.verison_time_stamp}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/js",
            f"{self.output_dir}/js/{self.verison_time_stamp}",
            dirs_exist_ok=True,
        )

        if self.redirection:
            shutil.copy("resources/.htaccess", f"{self.output_dir}/.htaccess")

        if os.path.isdir(f"{self.input_dir}/icon/"):
            shutil.copytree(
                f"{self.input_dir}/icon",
                f"{self.output_dir}/icon/{self.verison_time_stamp}",
                dirs_exist_ok=True,
            )

        if os.path.isdir(f"{self.input_dir}/img"):
            shutil.copytree(
                f"{self.input_dir}/img",
                f"{self.output_dir}/img/{self.verison_time_stamp}",
                dirs_exist_ok=True,
            )

    def __default_frontmatter(self):
        return {
            "title": "Page",
            "width": "85%",
            "icon": "page.webp",
            "ascii-font": self.config["font"]["ascii"],
        }

    def make(self):
        pages = []

        for file in tqdm.tqdm(self.files, desc="Tokeniser"):
            page = self.tokeniser.tokenise(os.path.join(self.input_dir, file + ".md"))
            page["file"] = file
            page["frontmatter"] = {
                **self.__default_frontmatter(),
                **page["frontmatter"],
            }

            pages.append(page)

        # print(pages[0])

        html_pages = {}
        for page in tqdm.tqdm(pages, desc="Compilser"):
            html_pages[page["file"]] = self.compiler.compile(
                page, self.time_stamp, self.verison_time_stamp
            )

        # print(html_pages)

        #####
        # LINKER
        #####

        self.__copy_resources()

        for file in html_pages:
            if "/" in file:
                os.makedirs(
                    os.path.join(self.output_dir, os.path.dirname(file)),
                    exist_ok=True,
                )

            with open(os.path.join(self.output_dir, file + ".html"), "w") as f:
                f.write(html_pages[file])
