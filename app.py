import streamlit as st
import os
import re
from PIL import Image
from streamlit_autorefresh import st_autorefresh
import subprocess

# ---- Helper Functions and Classes---- 
def is_fully_downloaded(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def get_images_from_directory(directory):
    stories = {}
    for story_name in os.listdir(directory):
        story_path = os.path.join(directory, story_name)
        if os.path.isdir(story_path):
            images = []
            for file_name in os.listdir(story_path):
                if file_name.endswith('.png'):
                    file_path = os.path.join(story_path, file_name)
                    if is_fully_downloaded(file_path):
                        images.append(file_path)
            if not images:
                continue
            images.sort(key=lambda x: int(re.search(r'@P(\d+).png', x).group(1)))
            stories[story_name] = images
    return stories

STORIES_DIRECTORY = os.path.join(os.getcwd(), "stories")
NUM_IMAGES = 12

# ---- Page Config----
st.set_page_config(page_title="Stable Diffusion", layout="wide", page_icon=":tada:")
st_autorefresh(interval=10000, key="image_counter")

# ---- Header Section ----
st.subheader("Orator Image Generation Engine")
st.title("v0.9")

# ---- Generate images button ----
if st.button("Generate images"):
    subprocess.call("python main.py", shell=True)

# ---- Generate PDF button ----
if st.button("Create PDF"):
    subprocess.call("python scripts\\create_json.py && python scripts\\create_pdf.py", shell=True)

# ---- Display stories ---- 
stories = get_images_from_directory(STORIES_DIRECTORY)
if stories:
    for story, images in stories.items():
        st.header(story)
        if st.button("View PDF", key=f"view_pdf_{story}"):
            path = f"pdf\\{story}.pdf"
            if not os.path.isfile(path):
                st.warning("Wait for all images to be generated!")
            else:
                subprocess.Popen([path], shell=True)
        with st.container():
            cols = st.columns(NUM_IMAGES)
            for col, image_path in zip(cols, images):
                image = Image.open(image_path)
                col.image(image, caption=os.path.basename(image_path), use_column_width='always')
