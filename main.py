import argparse
import time

from watchdog.observers import Observer

import src.downloader as dl
import src.handler as hdl
import src.page_maker as pm


def main():
    parser = argparse.ArgumentParser(
        prog="Simple Pages",
        description="This tool creates simple web pages from markdown like files",
        epilog="",
    )
    parser.add_argument(
        "input_dir", help="Input Directory (needs to contain at least a index.md)"
    )
    parser.add_argument("output_dir", help="Output Directory")
    parser.add_argument(
        "-c",
        "--continuous",
        default=False,
        required=False,
        action="store_true",
        help="Run continuously, watching for file changes in the input directory",
    )

    args = parser.parse_args()

    dl.get_default_resources()

    page_maker = pm.PageMaker(args.input_dir, args.output_dir)
    page_maker.make()

    if not args.continuous:
        return

    print("Watching for file changes")
    event_handler = hdl.Handler(page_maker)

    observer = Observer()
    observer.schedule(event_handler, args.input_dir, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
