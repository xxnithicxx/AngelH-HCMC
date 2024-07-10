from utils.helper import get_coze_data


class ContextAnalysis:
    def __init__(self):
        self.prompt = "Give me the context of the image."

    def analyze_context(self, image_url):
        """
        Analyze context based on prompt and image URL
        prompt: str
        image_url: str. Input image URL in format 'https://example.com/*.jpg'
        """

        coze_data = get_coze_data(
            self.prompt, image_url, "7385806741613297672")
        return coze_data["messages"][2]["content"]
