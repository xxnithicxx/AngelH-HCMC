from helper import get_coze_data

class ContextAnalysis:
    def __init__(self, context_classifier):
        self.prompt = "Give me the context of the image."

    def analyze_context(self, prompt, image_url):
        """
        Analyze context based on prompt and image URL
        prompt: str
        image_url: str. Input image URL in format 'https://example.com/*.jpg'
        """

        coze_data = get_coze_data(prompt, image_url, 7385806741613297672)
        return self.context_classifier.classify(coze_data, self.context_classifier.classifier)