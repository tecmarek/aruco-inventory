from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import blue
from reportlab.graphics import renderPDF

from svglib.svglib import svg2rlg
from io import StringIO
from PIL import Image

#--------------------------
# Generator settings
#--------------------------

page_margin = 10 #mm

tag_size = 10 #mm
tag_spacing = 2.5 #mm

tag_start_number = 0#

#--------------------------


def gen_apriltag_svg(width, height, pixel_array, size):
    def gen_rgba(rbga):
        (_r, _g, _b, _raw_a) = rbga
        _a = _raw_a / 255
        return f'rgba({_r}, {_g}, {_b}, {_a})'

    def gen_gridsquare(row_num, col_num, pixel):
        _rgba = gen_rgba(pixel)
        _id = f'box{row_num}-{col_num}'
        return f'\t<rect width="1" height="1" x="{row_num}" y="{col_num}" fill="{_rgba}" id="{_id}"/>\n'

    svg_text = '<?xml version="1.0" standalone="yes"?>\n'
    svg_text += f'<svg width="{size}" height="{size}" viewBox="0,0,{width},{height}" xmlns="http://www.w3.org/2000/svg">\n'
    for _y in range(height):
        for _x in range(width):
            svg_text += gen_gridsquare(_x, _y, pixel_array[_x, _y])
    svg_text += '</svg>\n'

    return svg_text



def calculate_number_of_elements(page_width, element_width, spacing, margin):
    # Calculate the effective width available for elements
    effective_width = page_width - 2 * margin

    # Calculate the total width occupied by one element and one spacing
    total_element_spacing_width = element_width + spacing
    
    # Calculate the number of elements that can fit
    num_elements = effective_width // total_element_spacing_width
    
    return int(num_elements)

def draw_elements_on_page(c, element_width, spacing, margin, num_col, num_row, start):

    grid_id = start
    # Iterate over the number of columns and rows
    for col in range(num_col):
        for row in range(num_row):
            # Calculate the x and y positions
            x = margin + col * (element_width + spacing)
            y = margin + row * (element_width + spacing)
            
            #Draw the element at the calculated position
            # c.rect(x*mm, y*mm, element_width*mm, element_width*mm, stroke=1, fill=0)

            # center_x = x + element_width / 2
            # center_y = y + element_width / 2

            # rect_id = f"{grid_id}"
            # c.drawCentredString(center_x*mm, center_y*mm, rect_id)


            # Adjust the drawing's size and position
            apriltag_number = str(grid_id).zfill(5)
            file = f"tag52_13_{apriltag_number}.png"

            with Image.open("tagStandard52h13/" + file, 'r') as im:

                width, height = im.size
                pix_vals = im.load()
                
                apriltag_svg = gen_apriltag_svg(width, height, pix_vals, str(tag_size)+"mm")

            assert apriltag_svg is not None, 'Error: Failed to create SVG.'


            drawing = svg2rlg(StringIO(apriltag_svg))

            drawing.width = element_width
            drawing.height = element_width
            drawing.scale(element_width / drawing.width, element_width / drawing.height)
            #drawing.translate(x, y)
            
            # Draw the SVG image at the calculated position
            renderPDF.draw(drawing, c, x*mm, y*mm)

            grid_id += 1


def main():
    canvas = Canvas("layouts/Layout.pdf", pagesize=A4)


    n_col = calculate_number_of_elements(A4[0]/mm, tag_size, tag_spacing, page_margin)
    n_row = calculate_number_of_elements(A4[1]/mm, tag_size, tag_spacing, page_margin)

    print("Generating page with - rows:" + str(n_row) + " cols:" + str(n_col))

    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(blue)

    draw_elements_on_page(canvas, tag_size, tag_spacing, page_margin, n_col, n_row, tag_start_number)

    canvas.save()

if __name__ == "__main__":
    main()
