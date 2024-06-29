# Package imports
from PIL import Image
import streamlit as st
from streamlit_carousel import carousel  # c2

# Local imports
from helper import is_video_file
from context import ImageClassifier

st.set_page_config(layout="wide")
st.title("Analysis App")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize all classes
context_classifier = ImageClassifier()


# Create columns
col1, col2 = st.columns([1, 1])

with st.container():
    st.header("Upload Image")
    uploaded_files = st.file_uploader("Choose an image file", accept_multiple_files=True, type=[
                                      "jpg", "jpeg", "png", 'gif', 'mp4', 'avi', 'mov', 'wmv'])

with col1:
    st.header("OCR and Description")

    # C1: Display image and video based on selection
    if uploaded_files:
        selected_image = st.selectbox(
            "Select an image to display", uploaded_files, format_func=lambda x: x.name)

        if is_video_file(selected_image.name):
            st.video(selected_image)
        else:
            col_images = st.columns(2)
            image = Image.open(selected_image)

            # logo_detection = LogoDetection()
            # human_detection = HumanDetection()

            # image_logo = logo_detection.create_bounding_box(image)
            # image_human = human_detection.create_bounding_box(image)

            # col_images[0].image(
            #     image_logo, caption=image_logo.name, use_column_width=True)
            # col_images[1].image(
            #     image_logo, caption=image_logo.name, use_column_width=True)
            # col_images[0].image(
            #     image_human, caption=image_human.name, use_column_width=True)
            # col_images[1].image(
            #     image_human, caption=image_human.name, use_column_width=True)

    # C2: Display image and video based on slider
        # image_description = get_image_caption(image)
        # st.write(image_description)

        # # Perform OCR
        # st.subheader("OCR Texts")
        # ocr_texts = perform_ocr(image)
        # for text in ocr_texts:
        #     st.write(text)


with col2:
    st.header("Analysis")

    if uploaded_files:
        # Analyze image information
        # ocr_results = ' '.join(ocr_texts)
        # analysis = analyze_image_information(image_description, ocr_results)
        # st.write(analysis)

        # 5. Display image location
        image_content = {}
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            image_content[uploaded_file.name] = context_classifier.classify(
                image)

        content = image_content.get(
            selected_image.name, "No content available for this image.")
        st.write(content)
