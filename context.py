import json
import torch
import requests
import os
import google.generativeai as genai
from enum import Enum
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

genai.configure(api_key="AIzaSyDtgra-DNQ9JooKGdG56OcwaiC-1E4yHBw")

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

# multi_model = genai.GenerativeModel('models/gemini-1.5-pro', safety_settings=safety_settings)

multi_model = genai.GenerativeModel(
    'models/gemini-1.5-flash-latest', safety_settings=safety_settings)
text_model = genai.GenerativeModel(
    'models/gemini-1.5-flash-latest', safety_settings=safety_settings)


class ClassificationPS(Enum):
    """Prompt templates for zero-shot image classification."""
    IMAGE_CLASSIFICATION = "You are given an image and a list of class labels. Classify the image given the class labels. Answer using a single word if possible. Here are the class labels: {classes}"
    IMAGE_DESCRIPTION = "What do you see? Describe any object precisely, including its type or class."
    CLASS_DESCRIPTION = "1. Describe what a {class_label} looks like in one or two sentences.\n2. How can you identify a {class_label} in one or two sentences?\n3. What does a {class_label} look like? Respond with one or two sentences.\n4. Describe an image from the internet of a {class_label}. Respond with one or two sentences.\n5. A short caption of an image of a {class_label}:"


# Ref: https://arxiv.org/pdf/2405.15668
# Assuming CLIP for encoder
model_name = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)

# Define class prompt templates
classes = ["bar club", "retaurant", "convinience store",
           "supermarket", "outdoor", "indoor"]

# The output feature length of the CLIP model is obtains from running the following code:
# output_feature_length = model.get_image_features(**inputs)
output_feature_length = torch.Size([1, 512])


def llm(prompt, image=None):
    """Generates text using the LLM model.

    Args:
        image: Input image.
        prompt: Prompt template.

    Returns:
        Generated text.
    """

    # Can't not set the temperature for the model because it is not supported
    # Will be changed later on.

    if image is None:
        result = text_model.generate_content([prompt])
    else:
        result = multi_model.generate_content([prompt, image])

    try:
        return result.candidates[0].content.parts[0].text
    except:
        print("The answer is not generated")
        return "No text generated"


def create_classifier(class_names, image, k=1):
    """Constructs zero-shot image classifier.

    Args:
        class_names: A list of class names.
        k: Number of class descriptions to be generated by the LLM.

    Returns:
        A zero-shot image classification model.
    """

    assert k >= 0

    weights = []
    for class_name in class_names:
        # Get the first 2 information from the class name
        # 1. Class name encoding
        # 2. Template encoding (Give a better result based on the authors)
        with torch.no_grad():
            class_name_encoding = model.get_text_features(
                processor(class_name, return_tensors="pt", padding=True).input_ids)
            template_encoding = model.get_text_features(
                processor(f"A photo of {class_name}", return_tensors="pt", padding=True).input_ids)

        llm_class_description = torch.zeros(output_feature_length)
        i = 0

        list_of_files = os.listdir("resource")
        # Check if the file exists
        # TODO: Include multiple files for the same class
        if f"{class_name}.txt" in list_of_files:
            llm_class_feature = open(f"resource/{class_name}.txt", "r").read()
            llm_class_description += model.get_text_features(
                processor(llm_class_feature, return_tensors="pt", padding=True, truncation=True).input_ids)
            i += 1

        for i in range(k):
            llm_class_feature = llm(
                ClassificationPS.CLASS_DESCRIPTION.value.format(classes=",".join(classes), class_label=class_name))

            # Write the description of the class to the file for later uses
            with open(f"resource/{class_name}.txt", "w") as f:
                f.write(llm_class_feature)

            llm_class_description += model.get_text_features(
                processor(llm_class_feature, return_tensors="pt", padding=True, truncation=True).input_ids)

        llm_class_description /= k  # Average the features

        class_feature = class_name_encoding + template_encoding + llm_class_description
        normalized_class_feature = class_feature / \
            torch.linalg.norm(class_feature)
        weights.append(normalized_class_feature.squeeze())

    return_model = {
        "weights": torch.stack(weights).transpose(0, 1),
        "class_names": class_names,
    }
    return return_model


def classify(image, classifier):
    """Performs zero-shot image classification.

    Args:
        image: Input testing image.
        classifier: A zero-shot classification model generated by create_classifier function.

    Returns:
        Predicted class name.
    """

    with torch.no_grad():
        image_encoding = model.get_image_features(
            processor(images=image, return_tensors="pt").pixel_values)
        image_encoding /= torch.linalg.norm(image_encoding)

        initial_prediction = llm(ClassificationPS.IMAGE_CLASSIFICATION.value.format(
            classes=",".join(classifier["class_names"]), class_label=""), image)
        prediction_encoding = model.get_text_features(
            processor(initial_prediction, return_tensors="pt", padding=True, truncation=True).input_ids)
        prediction_encoding /= torch.linalg.norm(prediction_encoding)

        image_description = llm(ClassificationPS.IMAGE_DESCRIPTION.value.format(
            classes=",".join(classifier["class_names"]), class_label=""), image)
        description_encoding = model.get_text_features(
            processor(image_description, return_tensors="pt", padding=True, truncation=True).input_ids)
        description_encoding /= torch.linalg.norm(description_encoding)

        query_feature = image_encoding + prediction_encoding + description_encoding
        query_feature /= torch.linalg.norm(query_feature)

        index = torch.argmax(torch.matmul(
            query_feature, classifier["weights"]))
        return classifier["class_names"][index.item()]


class ImageClassifier:
    def __init__(self, class_names=classes, k=1):
        self.class_names = class_names
        self.k = k
        self.classifier = create_classifier(class_names, k)

    def classify(self, image: Image.Image):
        return classify(image, self.classifier)
