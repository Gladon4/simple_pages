from watchdog.events import FileSystemEventHandler


class Handler(FileSystemEventHandler):
    def __init__(self, page_maker):
        self.page_maker = page_maker

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
            self.page_maker.setup()
            self.page_maker.make()
