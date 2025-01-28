import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from converter import Converter

converter = Converter()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
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
            converter.convert()


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "First argument: input directory; Second argument: output directory"
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    page_font = "JetBrains-Mono-Regular.ttf"
    ascii_font = "BonaNovaSC-Bold.ttf"

    converter.setup(input_dir, output_dir, page_font, ascii_font)
    converter.convert()

    # Initialize logging event handler
    event_handler = Handler()

    # Initialize Observer
    observer = Observer()
    observer.schedule(event_handler, input_dir, recursive=True)

    # Start the observer
    observer.start()
    try:
        while True:
            # Set the thread sleep time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
