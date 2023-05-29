from time import sleep

import openai
from openai.error import RateLimitError, APIError


class ChatGPT:
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo'):
        openai.api_key = api_key

        self.model = model

    def send_response(self, prompt: str):
        while True:
            try:
                answer = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.0
                )
                break
            except RateLimitError:
                continue
        sleep(5)
        return answer

    def send_responses(self, prompts: list):
        while True:
            try:
                answer = openai.ChatCompletion.create(
                    model=self.model,
                    messages=prompts,
                    temperature=1.0
                )
                break
            except RateLimitError or APIError:
                sleep(5)
                continue
        return answer
