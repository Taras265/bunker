import openai


class TextDavinci:
    def __init__(self, api_key: str, model: str = 'text-davinci-003'):
        openai.api_key = api_key

        self.model = model

    def send_response(self, prompt: str, max_tokens: int = 60):
        return openai.Completion.create(
            model=self.model,
            prompt=prompt,
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0
        )
