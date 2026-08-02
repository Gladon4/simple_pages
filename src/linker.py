import re

from typing_extensions import Optional

import src.utils as utils


class Linker:
    def __init__(self, config, all_files):
        self.config = config
        self.all_files = all_files
        self.pages: Optional[list[dict]] = None

        self.links = self.__link_map(self.all_files)

    def __link_map(self, files):
        links = {}

        for file in files:
            links[file] = file

            path_withot_ext = file.split(".")[0]
            if path_withot_ext not in links.keys():
                links[path_withot_ext] = file

            name_with_ext = file.split("/")[-1]
            if name_with_ext not in links.keys():
                links[name_with_ext] = file

            name_without_ext = file.split("/")[-1].split(".")[0]
            if name_without_ext not in links.keys():
                links[name_without_ext] = file

        return links

    def __replace_rendered(self, html_page):
        """
        ![[var|width]] -> becomes an image with path var and width width
        if it is a web page it becaomes an iframe ie an "image" of a web page
        """

        def replace_internal_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            width = match.group(2)  # Extract the optional name from [[var|size]]
            if width is None:
                width = "100%"

            target = self.links.get(var, var)
            if utils.is_link_local(target):
                target = f"/{target}"
            if utils.is_md(target):
                target = target.replace(".md", ".html")

            if utils.is_html(target):
                return f"<iframe src={target} height={width} width=100% style='border:none;' ></iframe>"
            elif utils.is_image(target):
                return f"<img src={target} alt='{var}' style='width:{width};' class='img'></img>"
            elif utils.is_video(target):
                return f"<video src={target} alt='{var}' autoplay loop muted style='width:{width};' class='video'></video>"
            else:
                return f"<iframe src={target} height=800px width={width} style='border:none;' ></iframe>"

        html_page = re.sub(
            r"!\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_internal_link, html_page
        )

        return html_page

    def __replace_link(self, html_page):
        """
        [[var|name]] -> becomes a link to var with the text of name
        if var is a local page name is by default the page title
        """

        def replace_link(match):
            var = match.group(1)  # Extract the variable name from [[var]]
            name = match.group(2)  # Extract the optional name from [[var|name]]

            target = self.links.get(var, var)

            if utils.is_link_local(target) and utils.is_md(target):
                if name is None:
                    page = utils.get_page_by_file(self.pages, target[:-3])
                    if page is None:
                        name = var
                    else:
                        name = page["frontmatter"]["title"]
                if self.config["behavior"]["redirection"] == "true":
                    target = target.replace(".md", "")
                else:
                    target = target.replace(".md", ".html")

                return f"<a href='/{target}'>{name}</a>"

            else:
                if utils.is_link_local(target):
                    target = f"/{target}"
                if name is None:
                    name = var

                return f"<a href='{target}'>{name}</a>"

        html_page = re.sub(
            r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", replace_link, html_page
        )

        return html_page

    def __replace_icon(self, html_page):
        """
        special case of image replacement
        [{name}] -> becomes an image with path name
        and class icon, which makes it the size of text
        """

        def replace_icons(match):
            name = match.group(1)
            target = self.links.get(name, name)

            if utils.is_link_local(target):
                target = f"/{target}"

            if not utils.is_image(target):
                return "Icon Not Image"

            return f"<img src={target} class='icon'></img>"

        html_page = re.sub(r"\[\{(.+?)\}\]", replace_icons, html_page)

        return html_page

    def __replace_tags(self, html_page):
        """
        [tag] -> becomes the local path to this file if existent
        """

        def replace_tag(match):
            tag = match.group(1)
            target = self.links.get(tag, tag)

            if utils.is_link_local(target):
                target = f"/{target}"

            return target

        html_page = re.sub(r"\[(.+?)\]", replace_tag, html_page)

        return html_page

    def link(self, html_page):
        html_page = self.__replace_rendered(html_page)
        html_page = self.__replace_icon(html_page)
        html_page = self.__replace_link(html_page)

        html_page = self.__replace_tags(html_page)

        return html_page
