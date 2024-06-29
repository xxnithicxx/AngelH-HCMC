import os
import json
from PIL import Image, ImageDraw, ImageFont
from hume import HumeBatchClient
from hume.models.config import FaceConfig


class FaceEmotionAnalyzer:
    def __init__(self, api_key, filepaths):
        self.client = HumeBatchClient(api_key)
        self.config = FaceConfig()
        self.filepaths = filepaths
        self.job = None

    def submit_job(self):
        self.job = self.client.submit_job(
            None, [self.config], files=self.filepaths)
        print(self.job)

    def await_completion(self):
        if self.job:
            self.job.await_complete()
            self.job.download_predictions("predictions.json")
            print("Predictions downloaded to predictions.json")
        else:
            print("Job not submitted. Please submit a job first.")

    @staticmethod
    def get_highest_emotion(emotions):
        highest_emotion = max(emotions, key=lambda x: x['score'])
        return highest_emotion['name'], highest_emotion['score']

    def visualize_predictions(self):
        with open('predictions.json') as f:
            data = json.load(f)

        for idx, prediction in enumerate(data):
            base_path = os.path.dirname(self.filepaths[0])
            image_path = os.path.join(
                base_path, prediction['source']['filename'])
            print(f"Processing image {idx}: {image_path}")

            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                print(f"Skipping non-image file: {image_path}")
                continue

            try:
                image = Image.open(image_path)
            except (FileNotFoundError, IOError) as e:
                print(f"Error opening image {image_path}: {e}")
                continue

            draw = ImageDraw.Draw(image)
            font_size = 75
            font = ImageFont.truetype("arial.ttf", font_size)

            face_count = 1
            for face in prediction['results']['predictions'][0]['models']['face']['grouped_predictions']:
                for face_data in face['predictions']:
                    box = face_data['box']
                    draw.rectangle(
                        [(box['x'], box['y']), (box['x'] + box['w'], box['y'] + box['h'])],
                        outline="red", width=20
                    )

                    emotion, score = self.get_highest_emotion(
                        face_data['emotions'])
                    draw.text((box['x'], box['y']), f'{face_count}: {emotion} ({score:.2f})',
                              fill="yellow", font=font)

                    face_count += 1

            image.save(f'image_with_emotion_{idx}.png', quality=95)

            for face_idx, face in enumerate(prediction['results']['predictions'][0]['models']['face']['grouped_predictions'], start=1):
                for face_data_idx, face_data in enumerate(face['predictions'], start=1):
                    emotion, score = self.get_highest_emotion(
                        face_data['emotions'])
                    print(
                        f'Person {face_idx}.{face_data_idx}: {emotion}({score:.2f})')

            print(f"Image with emotions saved as image_with_emotion_{idx}.png")


if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    filepaths = [
        "D:\GIT\HUME\\BZ1A0408.jpg",
        "D:\GIT\HUME\\BZ1A0464.jpg",
    ]

    analyzer = FaceEmotionAnalyzer(api_key, filepaths)
    analyzer.submit_job()
    analyzer.await_completion()
    analyzer.visualize_predictions()
