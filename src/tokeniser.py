class Tokeniser:
    def __init__(self, config):
        self.config = config

    @classmethod
    def get_args(cls, text: str):
        args = []
        while text.lstrip().startswith("\\"):
            end = 1
            while text[end] != "\\" and text[end] != "\n":
                end += 1
                if end == len(text):
                    break
            if end < len(text) and text[end] == "\\":
                end -= 1
            args.append(text[1:end])
            text = text[end + 1 :]

        args = list(map(str.strip, args))
        args = list(map(lambda s: str.split(s, " "), args))

        return args, text

    def tokenise(self, file_path):
        with open(file_path, "r") as file:
            data = file.read()

        data = self.__filter_comments(data)

        page = {}
        page["frontmatter"], start_line = self.__get_frontmatter(data)

        data = data.split("\n", start_line)[-1].lstrip()
        paragraphs = data.split("\n\n")

        page["paragraphs"] = []
        for paragraph in paragraphs:
            paragraph = paragraph.lstrip()
            par_type = "paragraph"
            type_args = []

            if paragraph.startswith("@"):
                split = paragraph.split("\n", maxsplit=1)
                if len(split) >= 2:
                    par_type, paragraph = split
                else:
                    par_type = split[0]
                    paragraph = ""

                par_type = par_type.lstrip("@")
                type_args = par_type.split(" ")
                par_type = type_args[0]
                type_args = type_args[1:]
                type_args = list(map(str.strip, type_args))

                if len(type_args) > 0:
                    type_args = ["type_args"] + type_args

            args, paragraph = Tokeniser.get_args(paragraph)

            if type_args != []:
                args.append(type_args)

            page["paragraphs"].append(
                {"type": par_type, "args": args, "text": paragraph}
            )

        return page

    def __get_frontmatter(self, data):
        frontmatter = {}
        if len(data.split("---")) < 3:
            return frontmatter, 0

        lines = data.split("\n")
        i = 1
        while "---" not in lines[i]:
            content = lines[i].split(":")
            frontmatter[content[0]] = content[1].lstrip()
            i += 1

        return frontmatter, i + 1

    def __filter_comments(self, data):
        index = 0
        while index < len(data):
            if data[index : index + 2] == "//":
                end = index + 1
                while data[end] != "\n":
                    end += 1
                data = data[:index] + data[end:]

            if data[index : index + 2] == "/*":
                end = index + 1
                while data[end : end + 2] != "*/":
                    end += 1
                data = data[:index] + data[end + 2 :]

            index += 1

        return data
