# TODO: Ignore comments


class Tokeniser:
    def __init__(self, config):
        self.config = config

    def tokenise(self, file_path):
        with open(file_path, "r") as file:
            data = file.read()

        page = {}
        page["frontmatter"], start_line = self.__get_frontmatter(data)

        data = data.split("\n", start_line)[-1].lstrip()
        paragraphs = data.split("\n\n")

        page["paragraphs"] = []
        for paragraph in paragraphs:
            par_type = "paragraph"
            type_args = []

            if paragraph.startswith("@"):
                par_type, paragraph = paragraph.split("\n", maxsplit=1)
                par_type = par_type.lstrip("@")
                type_args = par_type.split(" ")
                par_type = type_args[0]
                type_args = type_args[1:]
                type_args = list(map(str.strip, type_args))

                if len(type_args) > 0:
                    type_args = ["type_args"] + type_args

            args = paragraph.split("\\")
            if len(args) > 1:
                args = args[1:]
                tmp = args[-1].split("\n", maxsplit=1)
                args[-1] = tmp[0]
                paragraph = tmp[1]
                args = list(map(str.strip, args))
                args = list(map(lambda s: str.split(s, " "), args))
            else:
                args = []

            if type_args != []:
                args.append(type_args)

            page["paragraphs"].append(
                {"type": par_type, "args": args, "text": paragraph}
            )

        return page

    def __get_frontmatter(self, data):
        frontmatter = {}
        if len(data.split("---")) != 3:
            return frontmatter, 0

        lines = data.split("\n")
        i = 1
        while "---" not in lines[i]:
            content = lines[i].split(":")
            frontmatter[content[0]] = content[1]
            i += 1

        return frontmatter, i + 1
