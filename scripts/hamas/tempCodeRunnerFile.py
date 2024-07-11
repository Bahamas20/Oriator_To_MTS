        # # Calling API for add-new-page for each page
        # for page_number in range(len(file)):
            
        #     page = file.load_page(page_number)
            
        #     if page_number == len(file) - 1:
        #         current_page = Page(page,-1)
            
        #     else:
        #         current_page = Page(page,page_number)
            
        #     files = current_page.save_background_image(file)
        #     page_json = generate_page_json(current_page,character_name,story_id)
        #     # post_page_request(page_json,files)