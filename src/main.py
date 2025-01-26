from text_to_ascii import T2A
from parser import Parser

import os
import sys
import shutil
import time
import datetime

if __name__ == "__main__":
    assert len(sys.argv) == 2, "Directory need to be provided"
    dir = sys.argv[1]

    t2a = T2A("resources/fonts/BonaNovaSC-Bold.ttf", [20, 30, 40, 50])
    parser = Parser(dir, t2a)

    verison_time_stamp = int((time.time() * 1000) % 1000000)
    shutil.rmtree("export")
    os.makedirs("export", exist_ok=True)
    shutil.copytree(
        "resources/css", f"export/css/{verison_time_stamp}", dirs_exist_ok=True
    )

    time_stamp = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")

    for page in parser.pages:
        front_matter = parser.pages[page]["front_matter"]

        if "/" in page:
            os.makedirs(
                os.path.join("export/", os.path.dirname(page)), exist_ok=True
            )

        with open(f"export/{page}.html", "w") as f:
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

            for element in parser.pages[page]["elements"]:
                f.write(element)

            f.write(
                """
                <footer>
                    <hr>
                    <div>
                        <a href='/main.html'>Frontpage</a>
                        <br>
                        <p>Version from: {time_stamp}</p>
                    </div>
                </footer>
                """.format(
                    time_stamp=time_stamp
                )
            )
            f.write("</body>")
