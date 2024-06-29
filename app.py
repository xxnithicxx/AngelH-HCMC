from PIL import Image
import streamlit as st
from streamlit_carousel import carousel  # Ensure you have installed this library

from helper import is_video_file
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name='dzf1raeil',
    api_key='627966626163438',
    api_secret='86pSNB2FxH-_nnprwTDGzwzDJ-A'
)

st.set_page_config(layout="wide")
st.title("Analysis App")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class UI:
    def __init__(self):
        self.uploaded_files_dict = st.session_state.get('uploaded_files_dict', {})
        self.previous_uploaded_files = st.session_state.get('previous_uploaded_files', [])
        self.selected_file_name = st.session_state.get('selected_file_name', None)
    def handle_file_change(self):
        current_uploaded_files = st.session_state.uploaded_files
        if current_uploaded_files != self.previous_uploaded_files:
            for uploaded_file in current_uploaded_files:
                if uploaded_file.name not in self.uploaded_files_dict:
                    if not is_video_file(uploaded_file.name):
                        image = Image.open(uploaded_file)
                        img_byte_array = io.BytesIO()
                        image.save(img_byte_array, format=image.format)
                        img_byte_array = img_byte_array.getvalue()

                        upload_response = cloudinary.uploader.upload(img_byte_array)

                        if upload_response:
                            # st.success(f"Upload successful! URL: {upload_response['url']}")
                            item = {
                                "name": uploaded_file.name,
                                "image_path": image,
                                "image_url": upload_response["url"],
                                "predict": {
                                    "image1": image,
                                    "image2": image,  # Placeholder (modify as needed)
                                    "image3": image,  # Placeholder (modify as needed)
                                    "image4": image,  # Placeholder (modify as needed)
                                    "analysis": "content"
                                }
                            }
                            self.uploaded_files_dict[uploaded_file.name] = item
                            st.session_state.uploaded_files_dict = self.uploaded_files_dict

            self.previous_uploaded_files = current_uploaded_files
            st.session_state.previous_uploaded_files = self.previous_uploaded_files

    def run(self):
        with st.container():
            st.header("Upload Image or Video")
            st.file_uploader(
                "Choose a file", accept_multiple_files=True, type=[
                    "jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "wmv"
                ],
                on_change=self.handle_file_change, key="uploaded_files"
            )

        col1, col2 = st.columns([1, 1])
        with col1:
            st.header("Selected File")
            if self.uploaded_files_dict:
                self.selected_file_name = st.selectbox(
                    "Select a file", list(self.uploaded_files_dict.keys())
                )

                if is_video_file(self.selected_file_name):
                    st.video(self.selected_file_name)
                else:
                    chosen_item = self.uploaded_files_dict[self.selected_file_name]
                    st.image(chosen_item["image_path"], caption=self.selected_file_name, use_column_width=True)

        with col2:
            st.header("Analysis")
            if self.uploaded_files_dict:
                if self.selected_file_name:
                    chosen_item = self.uploaded_files_dict[self.selected_file_name]
                    st.write(chosen_item["predict"]["analysis"])


if __name__ == "__main__":
    main = UI()
    main.run()
