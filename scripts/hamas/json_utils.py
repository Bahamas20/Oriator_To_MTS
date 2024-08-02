import math
import os
import tempfile
import fitz
import json
from page import Page
from page_utils import generate_sample_page_json
from template_utils import *
from PIL import Image, ImageDraw, ImageFont

def create_json(template_file,price,gender):
    try:
        json_list = []
        file = fitz.open(template_file)   

        theme = "5b76955b-edbd-925c-3281-3a11a710a1b2"
        is_trending = False
        font_program1 = None
        font_program2 = None
        price = price
        gender = gender
        original_title = ''
        original_character_name = ''
        original_description = ''
        title = ''
        description = ''

        template_json= {
        "Title":title,
        "Description": description,
        "OriginalCharacterName": original_character_name,
        "OriginalTitle": original_title,
        "OriginalDescription": original_description,
        "ThemeId": theme,
        "IsTrending": str(is_trending).lower(),
        "FontProgram1": font_program1,
        "FontProgram2": font_program2,
        "Price": str(price),
        "Gender": str(gender)
    }
        json_list.append(template_json)

        # # Calling API for add-new-page for each page
        for page_number in range(len(file)):

                page = file.load_page(page_number)
                
                if page_number == len(file) - 1:
                    current_page = Page(page,-1)
                
                else:
                    current_page = Page(page,page_number)
                
                page_json = generate_sample_page_json(current_page)

                json_list.append(page_json)
        
        # Save the JSON list to a file
        output_file = "output.json"
        with open(output_file, 'w') as f:
            json.dump(json_list, f, indent=4)

        print(f"JSON data successfully saved to {output_file}")

    except Exception as e:
        print(f"An error occured: {e}")

def input_json(json_list,json_data_path):
    json_file = open(json_data_path)
    json_data = json.load(json_file)
    title = ''
    description = ''
    image_list = []

    for i in range(len(json_list)):
        print(f"Page number {i}")
        if i == 0:
            data =  json_list[i]
            title = os.path.splitext(os.path.basename(json_data_path))[0]
            original_title = title
            original_character_name = get_name(json_data)
            original_description = get_original_description(json_data)
            title = get_title(original_title,original_character_name)
            description = get_description(original_description,original_character_name)

            data['Title'] = title
            data['Description'] = description
            data['OriginalCharacterName'] = original_character_name
            data['OriginalTitle'] = original_title
            data['OriginalDescription'] = original_description
            json_list[i] = data
            print(data)
            
        
        elif i == 1:
            data = json_list[i]
            data['TextElement1.Text'] = title
            data = position_text(data)
            data = filtered_json(data)
            files = get_image(json_data, i-1, data)
            image_list.append(files)
            json_list[i] = data
            print(data)

        
        elif i == len(json_list) - 1:
            data =  json_list[i]
            data['TextElement1.Text'] = description
            data = position_text(data)
            data = filtered_json(data)
            files = get_image(json_data, -1, data)
            image_list.append(files)
            json_list[i] = data
            print(data)
        
        else:
            data = json_list[i]
            data = input_text(json_data,i-1,data)
            data = position_text(data)
            data = filtered_json(data)
            files = get_image(json_data, i-1, data)
            image_list.append(files)
            json_list[i] = data
            print(data)
    
    return json_list, image_list       

def input_text(json_data,page_number,data):
        text_json = json_data['pageInfo']        
        for j in range(4):
            text = data[f'TextElement{j+1}.Text']
            if text != '':
                if page_number % 2 != 0 and 5 <= page_number <= 27:
                    base_page_number = (page_number - 5) // 2 + 1
                    page_data = next((page for page in text_json if page['id'] == base_page_number), None)
                    
                    if page_data and 'text' in page_data:
                        page_text = page_data['text']
                        if page_text:
                            # Assuming we want to use the first text in the list for the element
                            data[f'TextElement{j+1}.Text'] = page_text[j].strip()
                    return data
        else:
            return data
    
def position_text(data):
    for i in range(4):
        text = data[f'TextElement{i+1}.Text']
        if text != '':
            font_size = int(data[f'TextElement{i+1}.FontSize'])
            font = data[f'TextElement{i+1}.FontProgram']
            font_path = f'fonts/{font}'
            line_height = int(data[f'TextElement{i+1}.LineHeight'])
            bbox_width = int(data[f'TextElement{i+1}.Width'])

            # Calculate the width of the text
            text = data[f'TextElement{i+1}.Text']
            total_text_width = calculate_text_width(text, font_path, font_size)
        
            num_lines = int(math.ceil(total_text_width / bbox_width))  # Round up to nearest whole number
            total_height = num_lines * line_height
            center = int(data[f'TextElement{i+1}.Centre'])
            new_top = center - (total_height / 2)

            # Adjust the bbox
            data[f'TextElement{i+1}.Top'] = int(new_top)
            return data
            
    else:
        return data

def calculate_text_width(text, font_path, font_size):
        font = ImageFont.truetype(font_path, font_size)
        dummy_image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_image)
        # Use textbbox to get the bounding box of the text
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]  # Width of the text

def filtered_json(data):
    filtered_data = {key: value for key, value in data.items() if 'Centre' not in key}
    return filtered_data


def get_image(json_data,page_number,data):
    text_json = json_data['pageInfo']
    page_height = int(data['PageHeight'])
    page_width = int(data['PageWidth'])

    if page_number == 0:
        tag = 'Front'
        page_data = next((page for page in text_json if page['id'] == tag), None)
        image_path = page_data['image']
        files = {
                'Image': ('norm_image_{}.png'.format(page_number), open(image_path, 'rb'), 'image/png'),
                'LowResImage': ('low_res_{}.jpeg'.format(page_number), open(image_path, 'rb'), 'image/jpeg')
        }
        return files
    elif page_number == -1:
        tag = 'Back'
        page_data = next((page for page in text_json if page['id'] == tag), None)
        image_path = page_data['image']
        files = {
                'Image': ('norm_image_{}.png'.format(page_number), open(image_path, 'rb'), 'image/png'),
                'LowResImage': ('low_res_{}.jpeg'.format(page_number), open(image_path, 'rb'), 'image/jpeg')
        }
        return files
    elif page_number % 2 != 0 and 5 <= page_number <= 27:
        base_page_number = (page_number - 5) // 2 + 1
        page_data = next((page for page in text_json if page['id'] == base_page_number), None)
        image_path = page_data['image']
        files = {
                'Image': ('norm_image_{}.png'.format(base_page_number), open(image_path, 'rb'), 'image/png'),
                'LowResImage': ('low_res_{}.jpeg'.format(base_page_number), open(image_path, 'rb'), 'image/jpeg')
        }
        return files
    else:
        empty_image = Image.new('RGB', (page_width,page_height), (255, 255, 255))
    
        # Save the empty image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file_path = tmp_file.name
            empty_image.save(tmp_file_path, format='PNG')


        files = {
            'Image': ('empty_image_{}.png'.format(page_number), open(tmp_file_path, 'rb'), 'image/png'),
            'LowResImage': ('empty_image_{}.png'.format(page_number), open(tmp_file_path, 'rb'), 'image/png')
        }
        return files











