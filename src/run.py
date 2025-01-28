import sys
from converter import Converter

if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "First argument: input directory; Second argument: output directory"
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    page_font = "JetBrains-Mono-Regular.ttf"
    ascii_font = "BonaNovaSC-Bold.ttf"

    converter = Converter()
    converter.setup(input_dir, output_dir, page_font, ascii_font)
    converter.convert()
