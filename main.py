import argparse
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import src.downloader as dl
from src.converter import Converter


class Handler(FileSystemEventHandler):
    def __init__(self, converter):
        self.converter = converter

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif (
            event.event_type == "created"
            or event.event_type == "modified"
            or event.event_type == "deleted"
        ):
            print(
                f"Event: {event.event_type}, file: {event.src_path}. Running converter"
            )
            self.converter.convert()

def main():
    parser = argparse.ArgumentParser(
                    prog='Simple Pages',
                    description='This tool creates simple web pages from markdown like files',
                    epilog='')
    parser.add_argument("input_dir", help="Input Directory (needs to contain at least a index.md)")
    parser.add_argument("output_dir", help="Output Directory")
    parser.add_argument("-r", "--redirection", default=False, required=False, action='store_true', 
                        help="If you are using redirection from /page to /page.html on your http server, set this")
    parser.add_argument("-c", "--continuous", default=False, required=False, action='store_true', 
                        help="Run continuously, watching for file changes in the input directory")

    args = parser.parse_args()

    dl.get_default_resources()

    converter = Converter(args.input_dir, 
                          args.output_dir,
                          args.redirection)
    converter.convert()

    if not args.continuous:
        return
        
    print("Watching for file changes")
    event_handler = Handler(converter)

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
