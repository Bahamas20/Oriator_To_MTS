from template_utils import post_template_request
from page_utils import post_page_request
from json_utils import create_json,input_json

def main(json_list, image_list):
    try:
        StoryTemplateId = ''
        for i in range(json_list):
            if i == 0:
                payload = json_list[i]
                # StoryTemplateId = post_template_request(payload)
                StoryTemplateID = "6755ae44-75c9-2b1a-a144-3a141a3095d9"
            else:
                payload = json_list[i]
                payload['StoryTemplateId'] = StoryTemplateId
                files = image_list[i]
                post_page_request(payload,files)


    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    pdf_file = '/Users/mohamedhamas/Desktop/Work/Oriator_To_MTS/templates/updated_pdf.pdf'
    json_list = create_json(pdf_file,5,0)
    # json_data_path = 'stories/sample/Jeremy and the Dark Forest.json'
    # json_list, image_list = input_json(json_list,json_data_path)
    # main(json_list,image_list)
