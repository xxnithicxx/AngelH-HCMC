# Requirements packages
# !pip install hume opencv-python matplotlib pillow
import os
import json
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

            fig, ax = plt.subplots(1)
            ax.imshow(image)

            face_count = 1
            for face in prediction['results']['predictions'][0]['models']['face']['grouped_predictions']:
                for face_data in face['predictions']:
                    box = face_data['box']
                    rect = patches.Rectangle(
                        (box['x'], box['y']), box['w'], box['h'], linewidth=2, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)

                    emotion, score = self.get_highest_emotion(
                        face_data['emotions'])
                    plt.text(box['x'], box['y'], f'{face_count}: {emotion} ({score: .2f})',
                             color="yellow", fontsize=8, weight='bold')

                    face_count += 1

            plt.axis('off')
            plt.title(f"Image {idx}")

            for face_idx, face in enumerate(prediction['results']['predictions'][0]['models']['face']['grouped_predictions'], start=1):
                for face_data_idx, face_data in enumerate(face['predictions'], start=1):
                    emotion, score = self.get_highest_emotion(
                        face_data['emotions'])
                    print(
                        f'Person {face_idx}.{face_data_idx}: {emotion}({score: .2f})')

            plt.savefig(f'image_with_emotion_{idx}.png',
                        bbox_inches='tight', pad_inches=0)
            plt.close()


if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    filepaths = [
        "C:\Study\CPP\HK9\AngleH\Heneiken\Beer\\0.jpg",
        "C:\Study\CPP\HK9\AngleH\Heneiken\Beer\\1.jpg",
    ]

    analyzer = FaceEmotionAnalyzer(api_key, filepaths)
    analyzer.submit_job()
    analyzer.await_completion()
    analyzer.visualize_predictions()
