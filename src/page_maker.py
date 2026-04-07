import configparser
import glob
import os
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

        self.tokeniser = tok.Tokeniser()
        self.compiler = cmp.Compiler()

        #  time_stamp = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
        self.verison_time_stamp = int((time.time() * 1000) % 1000000)

        self.files = glob.glob(f"{self.input_dir}/**/*.md", recursive=True)
        self.files = [
            "/".join(f.split("/")[len(self.input_dir.split("/")) :])[:-3]
            for f in self.files
        ]

        if "index" not in self.files:
            assert False, "index.md not present in input directory."

    def make(self):
        pages = []

        for file in tqdm.tqdm(self.files, desc="Tokeniser"):
            page = self.tokeniser.tokenise(os.path.join(self.input_dir, file + ".md"))
            pages.append(page)

        print(pages)
