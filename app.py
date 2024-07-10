# Package imports
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import streamlit as st
# Local imports
from utils.helper import is_video_file
from src.context import ContextAnalysis
from src.emotions import FaceEmotionAnalyzer
from src.marketing import DectectMarketing
from utils.secret_keys import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


cloudinary.config(
    cloud_name='dzf1raeil',
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# Initialize all classes
context_classifier = ContextAnalysis()
emotion_analyzer = FaceEmotionAnalyzer()
marketing_detector = DectectMarketing()

st.set_page_config(layout="wide")
st.title("Analysis App")

with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class UI:
    def __init__(self):
        self.uploaded_files_dict = st.session_state.get(
            'uploaded_files_dict', {})
        self.previous_uploaded_files = st.session_state.get(
            'previous_uploaded_files', [])
        self.selected_file_name = st.session_state.get(
            'selected_file_name', None)

        # list_of_folder = os.listdir("resource")
        # if "advertisement" in list_of_folder:
        #     for file in os.listdir("resource/advertisement"):
        #         os.remove(f"resource/advertisement/{file}")
        #     os.rmdir("resource/advertisement")

    def save_and_delete_file(self, uploaded_file):
        # Save the uploaded file
        file_path = f"static/downloads/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Read and display the image
        # image = Image.open(file_path)
        # st.image(image, caption='Uploaded Image')

        # Call the API
        image_emotion = emotion_analyzer.analyze_emotion(file_path)
        detect_marketing, marketing_product, drinking_person  = marketing_detector.detect_marketing(file_path)

        return image_emotion, detect_marketing, marketing_product, drinking_person

    def handle_file_change(self):
        current_uploaded_files = st.session_state.uploaded_files
        if current_uploaded_files != self.previous_uploaded_files:
            for uploaded_file in current_uploaded_files:
                if uploaded_file.name not in self.uploaded_files_dict:
                    if not is_video_file(uploaded_file.name):
                        image_emotion, detect_marketing, marketing_product, drinking_person = self.save_and_delete_file(uploaded_file)
                        image = Image.open(uploaded_file)
                        img_byte_array = io.BytesIO()
                        image.save(img_byte_array, format=image.format)
                        img_byte_array = img_byte_array.getvalue()

                        upload_response = cloudinary.uploader.upload(img_byte_array)

                        image_caption = context_classifier.analyze_context(
                            upload_response["url"])

                        if upload_response:
                            item = {
                                "name": uploaded_file.name,
                                "image_url": upload_response["url"],
                                "predict": {
                                    "image3": detect_marketing,
                                    "image4": image_emotion,
                                    "analysis": image_caption + "\n\n" + marketing_product + "\n\n" + drinking_person 
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
                    st.image(
                        chosen_item["predict"]['image4'], caption='', use_column_width=True)
                    st.image(
                        chosen_item["predict"]['image3'], caption='', use_column_width=True)

        with col2:
            st.header("Analysis")
            if self.uploaded_files_dict:
                if self.selected_file_name:
                    chosen_item = self.uploaded_files_dict[self.selected_file_name]

                    st.write(chosen_item["predict"]["analysis"])


if __name__ == "__main__":
    main = UI()
    main.run()
