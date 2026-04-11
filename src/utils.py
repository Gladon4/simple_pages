def is_image(file_path):
    image_extensions = [".png", ".jpg", ".jpeg", "webp", "gif", ".svg"]

    return any(file_path.endswith(ext) for ext in image_extensions)


def is_md(file_path):
    return file_path.endswith(".md")


def is_html(file_path):
    return file_path.endswith(".html")


def is_video(file_path):
    video_extensions = [".mp4", ".avi", ".mov", ".mkv"]

    return any(file_path.endswith(ext) for ext in video_extensions)


def is_link_local(link):
    return not link.startswith("http")


def get_page_by_file(pages, file):
    for page in pages:
        if page["file"] == file:
            return page

    return None
