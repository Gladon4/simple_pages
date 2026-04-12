import configparser
import datetime
import glob
import json
import os
import shutil

import tqdm

import src.compiler as cmp
import src.linker as lnk
import src.tokeniser as tok
import src.utils as utils


class PageMaker:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        default_config = configparser.ConfigParser()
        custom_config = configparser.ConfigParser()
        config = configparser.ConfigParser()

        default_config.read(os.path.join(os.getcwd(), "config.ini"))
        config.read_dict(default_config)

        if os.path.isfile(os.path.join(input_dir, "config.ini")):
            custom_config.read(os.path.join(input_dir, "config.ini"))
            config.read_dict(custom_config)

        self.config = config

        self.redirection = config["behavior"]["redirection"] == "true"
        self.default_page_font = config["font"]["regular"]
        self.default_bold_font = config["font"]["bold"]
        self.default_ascii_font = config["font"]["ascii"]

        self.time_stamp = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
        # self.verison_time_stamp = int((time.time() * 1000) % 1000000)

        self.md_files = glob.glob(f"{self.input_dir}/**/*.md", recursive=True)
        self.md_files = [
            "/".join(f.split("/")[len(self.input_dir.split("/")) :])[:-3]
            for f in self.md_files
        ]

        input_files = glob.glob(f"{self.input_dir}/**/*.*", recursive=True)
        input_files = [
            "/".join(f.split("/")[len(self.input_dir.split("/")) :])
            for f in input_files
        ]
        default_files = glob.glob("resources/**/*.*", recursive=True)
        default_files = [f.removeprefix("resources/") for f in default_files]

        self.all_files = input_files + default_files

        self.tokeniser = tok.Tokeniser(self.config)
        self.compiler = cmp.Compiler(self.config)
        self.linker = lnk.Linker(self.config, self.all_files)

        if "index" not in self.md_files:
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
            f"{self.output_dir}/css",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/media",
            f"{self.output_dir}/media",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            "resources/js",
            f"{self.output_dir}/js",
            dirs_exist_ok=True,
        )

        if self.redirection:
            shutil.copy("resources/.htaccess", f"{self.output_dir}/.htaccess")

        for media_file in [f for f in self.all_files if not utils.is_md(f)]:
            if not os.path.isfile(f"{self.input_dir}/{media_file}"):
                continue

            os.makedirs(
                os.path.dirname(f"{self.output_dir}/{media_file}"), exist_ok=True
            )
            shutil.copy(
                f"{self.input_dir}/{media_file}",
                f"{self.output_dir}/{media_file}",
            )

    def __default_frontmatter(self):
        return {
            "title": "Page",
            "width": "85%",
            "icon": "page.webp",
            "ascii-font": self.config["font"]["ascii"],
        }

    def __create_search_json(self, pages):
        search_json = []
        for page in pages:
            name = page["frontmatter"]["title"]
            path = f"/{page['file']}"
            if not self.redirection:
                path += ".html"

            search_json.append({"name": name, "path": path})

        with open(f"{self.output_dir}/pages.json", "w") as search_file:
            json.dump(search_json, search_file)

    def make(self):
        pages = []

        for md_file in tqdm.tqdm(self.md_files, desc="Tokeniser"):
            page = self.tokeniser.tokenise(
                os.path.join(self.input_dir, md_file + ".md")
            )
            page["file"] = md_file
            page["frontmatter"] = {
                **self.__default_frontmatter(),
                **page["frontmatter"],
            }

            pages.append(page)

        self.linker.pages = pages

        html_pages = {}
        for page in tqdm.tqdm(pages, desc="Compilser"):
            html_pages[page["file"]] = self.compiler.compile(page, self.time_stamp)

        for page_file in tqdm.tqdm(html_pages, desc="Linker   "):
            html_pages[page_file] = self.linker.link(html_pages[page_file])

        self.__copy_resources()
        self.__create_search_json(pages)

        for md_file in html_pages:
            if "/" in md_file:
                os.makedirs(
                    os.path.join(self.output_dir, os.path.dirname(md_file)),
                    exist_ok=True,
                )

            with open(os.path.join(self.output_dir, md_file + ".html"), "w") as f:
                f.write(html_pages[md_file])
