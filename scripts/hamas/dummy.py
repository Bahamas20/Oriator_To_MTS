import math
from PIL import Image, ImageDraw, ImageFont

def calculate_num_lines(text, font_path, font_size, bbox_width):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font at {font_path} could not be loaded.")
        return None
    
    dummy_image = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_image)

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        
        test_line = f"{current_line} {word}".strip()
        test_width = draw.textbbox((0, 0), test_line, font=font)[2]
        print(test_width)

        if test_width <= bbox_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return len(lines)

# Example usage
text = "THISTEXTMAXWIDTHMAXWIDTHTHISISTEXTMAXWIDTH"
font_path = '/Users/mohamedhamas/Desktop/Work/Oriator_To_MTS/fonts/Letters For Learners.ttf'
font_size = 21
bbox_width = 405  # Example bounding box width

num_lines = calculate_num_lines(text, font_path, font_size, bbox_width)
print(f"Number of lines: {num_lines}")
