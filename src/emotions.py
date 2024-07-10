import os
import json
from PIL import Image, ImageDraw, ImageFont
from hume import HumeBatchClient
from hume.models.config import FaceConfig

from utils.secret_keys import HUME_API_KEY


class FaceEmotionAnalyzer:
    def __init__(self):
        self.client = HumeBatchClient(HUME_API_KEY)
        self.config = FaceConfig()
        self.job = None

    def submit_job_client(self, image_path):
        try:
            with open(image_path, 'rb') as file:
                self.job = self.client.submit_job(
                    None, [self.config], files=[image_path])
        except FileNotFoundError as e:
            print(f"Error submitting job: {e}")

    def await_completion(self):
        if self.job:
            self.job.await_complete()
            self.job.download_predictions("static/data/predictions.json")
        else:
            print("Job not submitted. Please submit a job first.")

    @staticmethod
    def get_highest_emotion(emotions):
        highest_emotion = max(emotions, key=lambda x: x['score'])
        return highest_emotion['name'], highest_emotion['score']

    def visualize_predictions(self, image_paths):
        with open('static/data/predictions.json') as f:
            data = json.load(f)

        for idx, prediction in enumerate(data):
            base_path = os.path.dirname(image_paths)
            image_path = os.path.join(
                base_path, prediction['source']['filename'])
            # print(f"Processing image {idx}: {image_path}")

            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # print(f"Skipping non-image file: {image_path}")
                continue

            try:
                image = Image.open(image_path)
            except (FileNotFoundError, IOError) as e:
                print(f"Error opening image {image_path}: {e}")
                continue

            draw = ImageDraw.Draw(image)
            font_size = 35
            font = ImageFont.truetype("arial.ttf", font_size)

            face_count = 1
            for face in prediction['results']['predictions'][0]['models']['face']['grouped_predictions']:
                for face_data in face['predictions']:
                    box = face_data['box']
                    draw.rectangle(
                        [(box['x'], box['y']), (box['x'] +
                                                box['w'], box['y'] + box['h'])],
                        outline="red", width=2
                    )

                    emotion, score = self.get_highest_emotion(
                        face_data['emotions'])
                    draw.text((box['x'], box['y']), f'{face_count}: {emotion} ({score:.2f})', fill="yellow", font=font)

                    face_count += 1

            image.save(
                f'static/assets/emotion/{os.path.basename(image_paths)}', quality=95)
            return f'static/assets/emotion/{os.path.basename(image_paths)}'

    def analyze_emotion(self, image_path):
        self.submit_job_client(image_path)
        self.await_completion()
        return self.visualize_predictions(image_path)
