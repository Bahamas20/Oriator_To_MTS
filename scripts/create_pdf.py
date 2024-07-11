import fitz
import json
import os

class CustomPDF:
    def __init__(self, path=None):
        self.pdf = fitz.open(path)
    
    def get(self):
        """
        Get the pdf object

        :return: PDF object 
        """
        return self.pdf
    
    def get_page(self, page_num):
        """
        Get the page at specified page_num

        :return: Page at specified page_num 
        """
        return self.pdf[page_num]

    def copy_page(self, ref_pdf, start, end):
        """
        Copies the page in the specified page range inclusive

        :param ref_pdf: Reference pdf to copy from
        :param start: Start page
        :param end: End page
        """
        self.pdf.insert_pdf(ref_pdf, start, end)

    def insert_new_page(self, page_num, width, height):
        """
        Inserts empty page with specified width x height at page_num

        :param page_num: 1 before specified page to insert 
        :param width: Width of page
        :param height: Height of page
        :return: The created page object
        """
        return self.pdf.new_page(page_num, width=width, height=height)
    
    def save_pdf(self, path_to_save):
        """
        Saves the pdf at specified path

        :param path_to_save: Path to save the pdf 
        """
        self.pdf.save(path_to_save)

    def get_num_pages(self):
        """
        Get number of pages of pdf

        :return: Number of pages 
        """
        return self.pdf.page_count
    

class Page:
    def __init__(self, page):
        self.page = page

    @staticmethod    
    def get_center(bbox):
        """
        Gets the center coordinates of a bboz

        :param bbox: Bbox of text 
        :return: Tuple (x, y) representing the center coordinates of bbox
        """
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        return center_x, center_y
    
    @staticmethod
    def get_text_width(bbox_list):
        """
        Gets the maximum bbox width

        :param bbox_list: List of bboxes
        :return: Maximum width  
        """
        min_x, max_x = float("inf"), float("-inf")

        for bbox in bbox_list:
            min_x = min(min_x, bbox[0])
            max_x = max(max_x, bbox[2])

        return max_x - min_x

    @staticmethod 
    def get_text_height(text, fontfile, fontsize, specified_width):
        """
        Calculates the new height required for the new text box

        :param text: Text to insert
        :param font_name: Font of text
        :param font_size: Font size of text
        :param specified_width: Predetermined specified width
        :return: Height of new text box
        """
        dummy_doc = fitz.open()
        dummy_page = dummy_doc.new_page()
        dummy_page_obj = Page(dummy_page)
        INITIAL_HEIGHT = 10000
        used_px = dummy_page_obj.insert_text(fitz.Rect(0, 0, specified_width,
                                                       INITIAL_HEIGHT), text,
                                             fontsize, fontfile, (0, 0, 0), 1)
        rect_height = INITIAL_HEIGHT - used_px 
        dummy_doc.close()

        return rect_height
    
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

        # Sort from top to bottom, then left to right
        bbox_list.sort(key=lambda x: (x[1], x[0]))
    
        return bbox_list
    
    def get_image_rects(self):
        """
        Gets the list of image rects in page

        :return: List of rects 
        """
        images = self.page.get_images()
        bbox_list = []

        for image in images:
            rect = self.page.get_image_rects(image)[0]
            bbox_list.append(rect)

        # Sort from top to bottom, then left to right
        bbox_list.sort(key=lambda x: (x[1], x[0])) 

        return bbox_list
  
    def insert_text(self, rect, text, fontsize, fontfile, color, align):
        """
        Insert text into specified rectangle, centered in the rectangle

        :param text: Text to insert
        :param rect: Rectangle object to insert text in
        :param fontsize: Text size 
        :param fontfile: Path to font
        """
        fontname = fontfile.split("\\")[-1].split(".")[0].replace(" ", "")

        return self.page.insert_textbox(rect, text, fontsize=fontsize,
                                        fontname=fontname, fontfile=fontfile,
                                        color=color, align=align)
    
    def insert_img(self, rect, image_path):
        """
        Adds image to page in given rect.
        
        :param rect: Rect to insert image in
        :param image_path: Path to new image
        """
        self.page.insert_image(rect, filename=image_path)
    
    def get_fontname(self):
        """
        Get fontname of current text in page.

        :return: Fontname if page contains text, else returns None 
        """
        return NotImplemented 
    
    def get_fontsize(self):
        """
        Get fontsize of current text in page. (Assuming all text on page have same size)

        :return: Fontsize if page contains text, else returns None 
        """
        fontsize = None
        blocks = self.page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fontsize = span["size"]
                        break
                    if fontsize:
                        break
                if fontsize:
                    break
        
        return fontsize

    def get_text_color(self):
        """
        Get color of current text in page.

        :return: Text color in RGB format if page contains text, else returns None 
        """
        color = None
        blocks = self.page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = span["color"]
                        break
                    if color:
                        break
                if color:
                    break
        
        return None if not color else tuple(val / 255 for val in fitz.sRGB_to_rgb(color))
    
    def contains_text(self):
        """
        Checks whether current page contains text.

        :return: True if page contains text bboxes, False otherwise 
        """
        return True if self.page.get_text("text") else False
    
    def contains_images(self):
        """
        Checks whether current page contains images. 

        :return True if page contain image bboxes, False otherwise
        """
        return True if self.page.get_images() else False
    
    def get_char_image_rect(self):
        """
        Gets the Rect for character image

        :return: Rect of character image 
        """
        images = self.page.get_images()
        res = None

        for image in images:
            rect = self.page.get_image_rects(image)[0]
            if rect[0] > self.page.rect.x0:
                res = rect
        
        return res


def create_new_pdf(template_pdf_path, path_to_config):
    template_pdf = CustomPDF(template_pdf_path)
    new_pdf = CustomPDF()
    page_count = template_pdf.get_num_pages()

    with open(path_to_config, "r") as f:
        data = json.load(f)

    for page_num in range(page_count):
        ref_page = template_pdf.get_page(page_num)
        width = ref_page.rect.width
        height = ref_page.rect.height
        new_page = new_pdf.insert_new_page(page_num, width, height)
        ref_page_obj = Page(ref_page)
        new_page_obj = Page(new_page)

        if ref_page_obj.contains_images():
            rect_list = ref_page_obj.get_image_rects()
            content = data[f"{page_num + 1}"]["content"]
            i = 0
            for item in content:
                if item["type"] == "image":
                    path = item["data"]
                    rect = rect_list[i]
                    new_page_obj.insert_img(rect, path)
                    i += 1

        if ref_page_obj.contains_text():
            bbox_list = ref_page_obj.get_text_bbox()
            content = data[f"{page_num + 1}"]["content"]
            i = 0
            for item in content:
                if item["type"] == "text":
                    text = item["data"]
                    fontsize = ref_page_obj.get_fontsize()
                    fontfile = "..\\assets\\Sue Ellen Francisco.ttf" if page_num == 0 else "..\\assets\\Letters for Learners.ttf"
                    fontcolor = ref_page_obj.get_text_color()
                    bbox = bbox_list[i]
                    center_x, center_y = ref_page_obj.get_center(bbox)
                    textbox_width =  bbox[2] - bbox[0]
                    textbox_height = ref_page_obj.get_text_height(text, fontfile, fontsize, textbox_width)
                    align = 0 if page_num == 4 or page_num == 29 else 1

                    x0, y0, x1, y1 = center_x - textbox_width / 2, center_y - textbox_height / 2, center_x + textbox_width / 2, center_y + textbox_height / 2
                    OFFSET = 20 if page_num == 29 or page_num == 33 else 0
                    rect = fitz.Rect(x0, y0 + OFFSET, x1, y1 + OFFSET)

                    new_page_obj.insert_text(rect, text, fontsize, fontfile,
                                             fontcolor, align)
                    i += 1

    new_pdf.save_pdf(f"..\\pdf\\{data['story_name']}.pdf") 

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    pdf_template_path = "..\\templates\\template_1.pdf"
    path_to_stories = "..\\stories"
    stories = os.listdir(path_to_stories)
    story_count = len(stories)

    for i in range(story_count):
        story = stories[i]
        story_dir = os.path.join(path_to_stories, story)
        if os.path.isdir(story_dir):
            story_template_path = os.path.join(story_dir, f"template_{story}.json")
            if not os.path.isfile(story_template_path):
                raise ValueError("Story template file is missing!")
            create_new_pdf(pdf_template_path, story_template_path)

