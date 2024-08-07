# Suport code (lib) for label_printer.py
# Created by tecmarek 2024

from PIL import Image, ImageDraw, ImageFont
import cairosvg
import io


class label_generator:
    def __init__(self, tag_size_mm, font_path):
        self.tag_size = tag_size_mm
        self.font_path = font_path

        self.background_color = (255, 255, 255)  # White
        self.content_color = (0, 0, 0)  # Black

        # Printer settings:
        self.pixels_per_mm = 7.087

        self.label_width_small = 70
        self.label_width_large = 210

        self.label_height_18mm = 120
        self.label_height_24mm = 128

        self.large_label_text_padding_18mm = 6
        self.large_label_text_padding_24mm = 6

        self.cut_line_pos_18mm = 108
        self.cut_line_pos_24mm = 108


    def __gen_apriltag_svg(self, width, height, pixel_array):
        size = str(int(self.tag_size*self.pixels_per_mm))+"px"

        def gen_rgba(rbga):
            (_r, _g, _b, _raw_a) = rbga
            _a = _raw_a / 255
            return f'rgba({_r}, {_g}, {_b}, {_a})'

        def gen_gridsquare(row_num, col_num, pixel):
            _rgba = gen_rgba(pixel)
            _id = f'box{row_num}-{col_num}'
            return f'\t<rect width="1" height="1" x="{row_num}" y="{col_num}" fill="{_rgba}" id="{_id}" stroke-width="0"/>\n'

        svg_text = '<?xml version="1.0" standalone="yes"?>\n'
        svg_text += f'<svg width="{size}" height="{size}" viewBox="0,0,{width},{height}" xmlns="http://www.w3.org/2000/svg">\n'
        for _y in range(height):
            for _x in range(width):
                svg_text += gen_gridsquare(_x, _y, pixel_array[_x, _y])
        svg_text += '</svg>\n'

        return svg_text
    
    def _gen_apriltag_png(self, tag_number):
        apriltag_number = str(tag_number).zfill(5)
        file = f"tag52_13_{apriltag_number}.png"

        with Image.open("apriltag-imgs/tagStandard52h13/" + file, 'r') as im:
            width, height = im.size
            pix_vals = im.load()
            
            apriltag_svg = self.__gen_apriltag_svg(width, height, pix_vals)

        assert apriltag_svg is not None, 'Error: Failed to create SVG.'

        apriltag_png_data = cairosvg.svg2png(bytestring=apriltag_svg)

        return Image.open(io.BytesIO(apriltag_png_data)).convert("RGBA")
    

    def make_small_label(self, media_width, number_of_lines, text_size, tag_number, text): # Text is array

        # media width setting -> setting label_height
        if media_width == "24mm":
            label_height = self.label_height_24mm
            cut_line_pos = self.cut_line_pos_24mm
        elif media_width == "18mm":
            label_height = self.label_height_18mm
            cut_line_pos = self.cut_line_pos_18mm

        label_width = self.label_width_small

        apriltag_text_padding = 4

        font = ImageFont.truetype(self.font_path, text_size)
        

        label_image = Image.new('RGB', (label_width, label_height), self.background_color)
        draw = ImageDraw.Draw(label_image)

        draw.fontmode = "1" # Only 2 color mode no aliasing

        # Generate Apriltag an place it on image
        apriltag_png = self._gen_apriltag_png(tag_number)

        apriltag_png_width, apriltag_png_height = apriltag_png.size
        apriltag_png_position = ((label_width - apriltag_png_width) // 2, 0)  # Center Tag on Label -> No top margin so place it right at 0

        label_image.paste(apriltag_png, apriltag_png_position, apriltag_png)

        text_total_height = cut_line_pos - apriltag_png_height - apriltag_text_padding

        text_height = text_total_height // number_of_lines


        for i in range(number_of_lines):
            text_bbox = draw.textbbox((0, 0), text[i], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_pos_y = apriltag_png_height + apriltag_text_padding + text_height*i
            #print("Text: " + str(i) + " - pos_y: " + str(text_pos_y))
            text_position = (label_width // 2 - text_width // 2, text_pos_y)
            draw.text(text_position, text[i], fill=self.content_color, font=font)
            
        # Draw cut line to aid in cutting the label to the correct size
        draw.line((0, cut_line_pos, label_width, cut_line_pos), fill=self.content_color, width=1)

        return label_image
    

    def make_large_label(self, media_width, cut_line, number_of_lines, text_size, tag_number, text): # Text is array

        # media width setting -> setting label_height
        if media_width == "24mm":
            label_height = self.label_height_24mm
            text_padding = self.large_label_text_padding_24mm
            cut_line_pos = self.cut_line_pos_24mm
        elif media_width == "18mm":
            label_height = self.label_height_18mm
            text_padding = self.large_label_text_padding_18mm
            cut_line_pos = self.cut_line_pos_18mm

        # No cut line so space everything for label height
        if not cut_line:
            cut_line_pos = label_height

        label_width = self.label_width_large

        apriltag_text_padding = 10

        font = ImageFont.truetype(self.font_path, text_size)
        

        label_image = Image.new('RGB', (label_width, label_height), self.background_color)
        draw = ImageDraw.Draw(label_image)

        draw.fontmode = "1" # Only 2 color mode no aliasing

        # Generate Apriltag an place it on image
        apriltag_png = self._gen_apriltag_png(tag_number)

        apriltag_png_width, apriltag_png_height = apriltag_png.size
        apriltag_png_position = (0, (cut_line_pos - apriltag_png_height) // 2)  # Center Tag on Label -> No left margin so place it right at 0

        label_image.paste(apriltag_png, apriltag_png_position, apriltag_png)

        # Calculate text x spacing
        text_total_width = label_width - apriltag_png_width - apriltag_text_padding
        text_x_offset = apriltag_png_width + apriltag_text_padding

        # Calculate text y spacing for top and bottom of text block
        total_text_height = sum(draw.textbbox((0, 0), text[i], font=font)[3] - draw.textbbox((0, 0), text[i], font=font)[1] for i in range(number_of_lines))
        total_padding_height = text_padding * (number_of_lines - 1)
        required_height = total_text_height + total_padding_height
        text_block_padding = (cut_line_pos - required_height) // 2


        text_pos_y = text_block_padding
        for i in range(number_of_lines):
            text_bbox = draw.textbbox((0, 0), text[i], font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_position = (text_total_width // 2 - text_width // 2 + text_x_offset, text_pos_y)
            draw.text(text_position, text[i], fill=self.content_color, font=font)
            text_pos_y += text_height + text_padding
            
        # Draw cut line to aid in cutting the label to the correct size
        # Only when enabled -> not needed for XL labels 
        if cut_line:
            if media_width == "24mm": # Drawn top line only on 24mm as there is only a very small margin with 18mm tapes
                draw.line((0, 0, label_width, 0), fill=self.content_color, width=1)
            draw.line((0, cut_line_pos, label_width, cut_line_pos), fill=self.content_color, width=1)

        return label_image