import sys
from converter import Converter

if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "First argument: input directory; Second argument: output directory"
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    default_page_font = "JetBrains-Mono-Regular.ttf"
    default_bold_font = "JetBrains-Mono-ExtraBold.ttf"
    default_ascii_font = "JetBrains-Mono-Regular.ttf"

    converter = Converter()
    converter.setup(input_dir, output_dir, default_page_font, default_bold_font, default_ascii_font)
    converter.convert()
