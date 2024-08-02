import os
import re
import tempfile
import fitz
import math
from PIL import Image, ImageDraw, ImageFont

class Page:

    def __init__(self,page,page_number,json_data=None,text=None,images_path=None):
        self.page = page
        self.page_number = page_number
        self.json_data = json_data
        self.text = text
        self.images_path = images_path
    
    def get_page_type(self):
        if self.page_number == 0:
            return 0
        elif self.page_number == -1:
            return 1
        else:
            return 2
    
    def get_page_width(self):
        return int(self.page.rect.width)

    def get_page_height(self):
        return int(self.page.rect.height)
    
    def get_text_boxes_info(self):
        """
        Gets detailed information about text bounding boxes on the page.

        :return: List of dictionaries, each containing information about a text box
        """
        text_boxes_info = []
        blocks = self.page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        
                        bbox = span["bbox"]
                        text = span["text"]
                        font_size = span.get("size", None) 
                        font = self.get_font(span.get("font", None))
                        stroke_width = None
                        text_align = 'center'
                        line_height = font_size * 1.2 
                        color_value = self.get_color(span.get("color", None))
                        width = (bbox[2] - bbox[0]) + 5
                        top = bbox[1]
                        left = bbox[0]
                        center_y = (bbox[1] + bbox[3]) / 2


                        text_box_info = {
                            "bbox": bbox,
                            "text": text,
                            "font_size": int(font_size),
                            "font": font,
                            "stroke_width": stroke_width,
                            "text_align": text_align,
                            "line_height": int(line_height),
                            "text_color": color_value,
                            "width": int(width),
                            "top": int(top),
                            "left": int(left),
                            "center": int(center_y)
                        }
                        text_boxes_info.append(text_box_info)


        text_boxes_info.sort(key=lambda x: (x["top"], x["left"]))

        return text_boxes_info
   
    def input_text(self,text_box_list):
        text_json = self.json_data['storyText']
        page_number = self.page_number
        if page_number == 0 or page_number == -1:
            text_box_list[0]['text'] = self.text
            return text_box_list

        if page_number % 2 != 0 and 5 <= page_number <= 27:
            base_page_number = (page_number - 5) // 2 + 1
            pattern = re.compile(rf"(?:Page {base_page_number}.*?\n)(.+?[.!?])", re.DOTALL) 
            match = pattern.search(text_json)
            print(match.group(1).strip() )
            if match:
                text_box_list[0]['text'] = match.group(1).strip() 
                return text_box_list
        else:
                return text_box_list
        
    def position_text(self,text_box_list):
        if self.contains_text():
            for i in range(len(text_box_list)):
                font_size = text_box_list[i].get('font_size')  # Default to 12 if not found
                font = text_box_list[i].get('font')  # Default font path
                font_path = f'fonts/{font}'
                line_height = text_box_list[i].get('line_height')
                bbox_width = text_box_list[i].get('width')

                # Calculate the width of the text
                text = text_box_list[i]['text']
                total_text_width = self.calculate_text_width(text, font_path, font_size)


                # Calculate the number of lines
        
                num_lines = int(math.ceil(total_text_width / bbox_width))  # Round up to nearest whole number
                total_height = num_lines * line_height
                center = text_box_list[i]['center']
                new_top = center - (total_height / 2)

                # Adjust the bbox
                text_box_list[i]['top'] = int(new_top)

            return text_box_list
        else:
            return text_box_list

    def calculate_text_width(self,text, font_path, font_size):
        font = ImageFont.truetype(font_path, font_size)
        dummy_image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_image)
        # Use textbbox to get the bounding box of the text
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]  # Width of the text
        
    def get_font(self,font):
        if font == 'SueEllenFrancisco':
            return 'Sue Ellen Francisco.ttf'
        elif font == 'LettersforLearners':
            return 'Letters For Learners.ttf'
        else:
            return None
    
    def get_color(self,color_value):
        if color_value is not None:
            return f"#{color_value:06x}"
        else:
            return None

    def resize_image(self,image_path, output_size):
        with Image.open(image_path) as img:
            resized_img = img.resize(output_size)
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f'resized_image_{os.path.basename(image_path)}')
            resized_img.save(temp_path, format='PNG')
            return temp_path
           
    def get_background_img(self):
        image_list = self.page.get_images()
        page_number = self.page_number
        resized_width = self.get_page_width()
        resized_height = self.get_page_height()

        if image_list and (page_number % 2 == 0 and 6 <= page_number <= 28):
            for img in image_list:
                xref = img[0]  
                width = img[2]
                height = img[3]

                if width == 1536 and height == 1536:
                    base_page_number = (page_number - 5) // 2 + 1
                    background_image_path = f'{self.images_path}/@P{base_page_number}.png'
                    resized_image_path = self.resize_image(background_image_path, (resized_width, resized_height))

                    files = {
                            'Image': ('norm_image_{}.png'.format(xref), open(resized_image_path, 'rb'), 'image/png'),
                            'LowResImage': ('low_res_{}.jpeg'.format(xref), open(resized_image_path, 'rb'), 'image/jpeg')
                    }
        
                    return files
        elif image_list and (page_number == 0 or page_number == -1):

                if page_number == 0:
                    text = 'FRONT'
                else:
                    text = 'BACK'

                background_image_path = f'{self.images_path}/@{text}.png'
                resized_image_path = self.resize_image(background_image_path, (resized_width, resized_height))

                files = {
                        'Image': ('norm_image_{}.png'.format(page_number), open(resized_image_path, 'rb'), 'image/png'),
                        'LowResImage': ('low_res_{}.jpeg'.format(page_number), open(resized_image_path, 'rb'), 'image/jpeg')
                }
                    
                return files
        else:
            try:
                # Create a blank white image 
                empty_image = Image.new('RGB', (resized_width,resized_height), (255, 255, 255))
                
                # Save the empty image to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file_path = tmp_file.name
                    empty_image.save(tmp_file_path, format='PNG')


                files = {
                    'Image': ('empty_image_{}.png'.format(page_number), open(tmp_file_path, 'rb'), 'image/png'),
                    'LowResImage': ('empty_image_{}.png'.format(page_number), open(tmp_file_path, 'rb'), 'image/png')
                }

                os.remove(tmp_file_path)  # Clean up temporary file

                return files
            
            except Exception as e:
                print(f"Error creating empty image: {e}")
   

    def downsize_img(image_path, output_path, size=(512, 512)):
        """
        Down-sizes an image to the specified size and saves it to the output path.
        
        :param image_path: Path to the input image.
        :param output_path: Path to save the down-resized image.
        :param size: Tuple specifying the desired size (width, height). Default is (512, 512).
        """
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Resize the image
            img_downres = img.resize(size, Image.LANCZOS)
            
            # Save the resized image
            img_downres.save(output_path, "PNG")
            print(f"Image saved to {output_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_text_bbox(self):
        """
        Gets the list of text bboxes in page

        :return: List of bboxes 
        """
        bbox_list = []
        blocks = self.page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox_list.append(span["bbox"])


        bbox_list.sort(key=lambda x: (x[1], x[0]))
    
        return bbox_list
    
    def contains_images(self):
        """
        Checks whether current page contains images. 

        :return True if page contain image bboxes, False otherwise
        """
        return True if self.page.get_images() else False
    
    def contains_text(self):
        """
        Checks whether current page contains text.

        :return: True if page contains text bboxes, False otherwise 
        """
        return True if self.page.get_text("text") else False
    