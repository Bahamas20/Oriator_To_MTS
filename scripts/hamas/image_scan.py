import os
import base64

def encode_files_to_base64(folder_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each file in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it is a file (and not a directory)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                # Read the file content and encode it to base64
                encoded_content = base64.b64encode(file.read()).decode('utf-8')
                
                # Define the path for the output text file
                output_file_path = os.path.join(output_folder, f"{filename}.txt")
                
                # Write the base64 encoded content to the text file
                with open(output_file_path, 'w') as output_file:
                    output_file.write(encoded_content)

# Specify the folder paths
input_folder_path = 'stories/sample/images/small'
output_folder_path = 'stories/sample/images/text'

# Encode files and save the base64 encoded content to text files
encode_files_to_base64(input_folder_path, output_folder_path)
