from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random


class T2A:
    def __init__(self, font_path, font_sizes):
        self.font_path = font_path
        self.fonts = {}
        for size in font_sizes:
            self.fonts[size] = ImageFont.truetype(font_path, size)

    def string_to_ascii(self, input_string, font_size, fade_str=1.0):
        try:
            if font_size not in self.fonts.keys():
                self.fonts[font_size] = ImageFont.truetype(self.font_path, font_size)

            font = self.fonts[font_size]

            # Determine the size of the image needed to render the text
            text_width, text_height = int(font.getlength(input_string)), font_size
            image = Image.new("L", (text_width, text_height), color=255)

            # Draw the text onto the image
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), input_string, font=font, fill=0)  # Black text

            img_array = np.array(image)

            # Identify rows where not all pixels are white (255)
            rows_with_content = ~(img_array == 255).all(axis=1)

            # Identify columns where not all pixels are white (255)
            columns_with_content = ~(img_array == 255).all(axis=0)

            # Find the bounding box of non-white content
            row_start, row_end = (
                rows_with_content.argmax(),
                len(rows_with_content) - rows_with_content[::-1].argmax(),
            )
            col_start, col_end = (
                columns_with_content.argmax(),
                len(columns_with_content) - columns_with_content[::-1].argmax(),
            )

            # Crop the image to the bounding box
            img_array = img_array[row_start:row_end, col_start:col_end]

            # img_array = np.array(image)
            height, width = img_array.shape

            for y in range(height):
                fade_factor = (1 - (y / height)) * (255 * fade_str)
                img_array[y, :] = np.clip(img_array[y, :] + fade_factor, 0, 255)

            image = Image.fromarray(img_array)
            # image.show()

            # Convert image to ASCII characters
            pixels = image.load()
            ascii_chars = "@%#*+=-:. "
            num_chars = len(ascii_chars)

            ascii_art = ""
            for y in range(image.height):
                for x in range(image.width):
                    brightness = pixels[x, y] / 255  # Normalize to 0-1
                    if brightness <= 0.95:
                        brightness += random.random() * 0.1 - 0.05
                    ascii_art += ascii_chars[int(brightness * (num_chars - 1))]
                ascii_art += "\n"

            return ascii_art

        except Exception as e:
            print(f"Error: {e}")
