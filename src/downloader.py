"""
Here are donwloads of default resources that I don't want to include like fonts.
"""
import urllib.request
import zipfile
import shutil
import os
import tqdm

TEMP_PATH = os.path.join(os.getcwd(), "temp")

FONT_PATH = os.path.join(os.getcwd(), "resources/fonts")
DEFAULT_FONTS = ["JetBrainsMono-Regular.ttf", "JetBrainsMono-ExtraBold.ttf",]
JETBRAINS_MONO_LINK = "https://download.jetbrains.com/fonts/JetBrainsMono-2.304.zip"

def get_default_resources():
    make_temp_dir()

    if any([font not in os.listdir(FONT_PATH) for font in DEFAULT_FONTS]):
        get_default_fonts()

    remove_temp_dir()

def make_temp_dir():
    os.makedirs(TEMP_PATH, exist_ok=True)

def remove_temp_dir():
    shutil.rmtree(TEMP_PATH)

def get_default_fonts():
    pbar = tqdm.tqdm(total=3, desc="Downloading Default Fonts")

    zip_path = os.path.join(TEMP_PATH, "JetBrainsMono.zip")
    urllib.request.urlretrieve(JETBRAINS_MONO_LINK, zip_path)
    pbar.update(1)

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        for font in DEFAULT_FONTS:
            zip_file.extract(f"fonts/ttf/{font}", TEMP_PATH)
    pbar.update(1)
    
    for font in DEFAULT_FONTS:
        shutil.copy(os.path.join(TEMP_PATH, f"fonts/ttf/{font}"), FONT_PATH)
    pbar.update(1)
    
