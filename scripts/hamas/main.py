import json
import time
import fitz
from template_utils import generate_template_json,post_template_request
from page_utils import generate_page_json,post_page_request
from page import Page


def main(pdf_file,json_data_path,images_path):
    try:
        file = fitz.open(pdf_file)   

        # Calling API for create-new-storytemplate
        json_file = open(json_data_path)
        json_data = json.load(json_file)
        theme_id = "5b76955b-edbd-925c-3281-3a11a710a1b2" # theme id for resillience
        is_trending = False
        price = 5
        gender = 0

        # creates a new story template and gets the template id
        template_json = generate_template_json(json_data,theme_id,is_trending,price,gender)

        story_id = post_template_request(template_json)
        # story_id = 'e0583031-0bb3-c540-d02b-3a13c67449db'
        time.sleep(2)
        character_name = template_json['OriginalCharacterName']
        title = template_json['Title']
        description = template_json['Description']
     
        # # Calling API for add-new-page for each page
        for page_number in range(len(file)):
            
            page = file.load_page(page_number)
            
            if page_number == len(file) - 1:
                current_page = Page(page,-1,json_data,description,images_path)
            
            else:
                current_page = Page(page,page_number,json_data,title,images_path)
            
            files = current_page.get_background_img()
            print(f"Page number {page_number}")
            page_json = generate_page_json(current_page,character_name,story_id)
            post_page_request(page_json,files)

    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    pdf_file = 'scripts/hamas/sample.pdf'
    json_data_path = 'stories/toy/Jeremy loses and finds his Teddy.json'
    images_path = 'stories/toy/images'
    main(pdf_file,json_data_path,images_path)
