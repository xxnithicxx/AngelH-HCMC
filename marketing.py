import io
import os
import json
import torch
import cloudinary
import cloudinary.api
import cloudinary.uploader
from ultralytics import YOLO
from PIL import Image, ImageOps, ImageDraw

from helper import get_coze_data
from secret_key import ROBOFLOW_API_KEY, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name='dzf1raeil',
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)


class DectectMarketing:
    def __init__(self):
        self.model = YOLO("weights/best.pt")

    def resize_bbox(self, image, bboxs):
        original_width, original_height = image.width, image.height

        # Resized dimensions (as per your setup)
        resized_width, resized_height = 640, 480

        # Calculate scale factors
        width_scale = original_width / resized_width
        height_scale = original_height / resized_height

        # Adjust bbox coordinates
        adjusted_bboxs = []
        for bbox in bboxs:
            adjusted_bbox = {
                'xmin': round(bbox['xmin'] * width_scale, 1),
                'ymin': round(bbox['ymin'] * height_scale, 1),
                'xmax': round(bbox['xmax'] * width_scale, 1),
                'ymax': round(bbox['ymax'] * height_scale, 1),
                # Assuming you want to keep the class label unchanged
                'class': bbox['class']
            }
            adjusted_bboxs.append(adjusted_bbox)

        return adjusted_bboxs

    def get_predictions(self, result):
        preds = []
        for r in result:
            boxes = r.boxes
            for box in boxes:
                pred = {}
                # get box coordinates in (left, top, right, bottom) format
                b = box.xyxy[0]
                c = box.cls
                pred['xmin'] = int(b[0])
                pred['ymin'] = int(b[1])
                pred['xmax'] = int(b[2])
                pred['ymax'] = int(b[3])
                pred['class'] = self.model.names[int(c)]
                preds.append(pred)

        return preds

    def detect_marketing(self, image_path):
        img = Image.open(image_path)
        image = img.copy()
        image = image.resize((640, 640))
        results = self.model(image, conf=0.35,)

        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format=img.format)
        img_byte_array = img_byte_array.getvalue()
        upload_response = cloudinary.uploader.upload(
            img_byte_array)

        url_image = upload_response['url']

        preds = self.get_predictions(results)
        draw = ImageDraw.Draw(image)
        for pred in preds:
            draw.rectangle(
                [(pred['xmin'], pred['ymin']), (pred['xmax'], pred['ymax'])],
                outline="red", width=2
            )
            draw.text((pred['xmin'], pred['ymin']), pred['class'],
                      fill="yellow")
        image.save(
            f'resource/advertisement/{os.path.basename(image_path)}', quality=95)

        bounding_box = [pred for pred in preds if "-brand" in pred['class']]
        promoter_person = [pred for pred in preds if "person" in pred['class'] or "-prometer" in pred['class']]

        cozy_data_promoter = get_coze_data(
            promoter_person, url_image, bot_id="7386091173783388161")
        
        # print(cozy_data_count)

        if not bounding_box:
            cozy_data_promotion = "There is no promotion items in this image."

            return f'resource/advertisement/{os.path.basename(image_path)}', cozy_data_promotion, cozy_data_promoter["messages"][2]["content"]
        else:
            cozy_data_promotion = get_coze_data(
                bounding_box, url_image, bot_id="7385922072989777927")
            
            return f'resource/advertisement/{os.path.basename(image_path)}', cozy_data_promotion["messages"][2]["content"], cozy_data_promoter["messages"][2]["content"]
