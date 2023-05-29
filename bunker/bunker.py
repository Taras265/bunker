from random import choice
from time import sleep

from bunker.bots import Bots
from bunker.characteristics import THREAT
from chat_gpt import ChatGPT
from text_davinci import TextDavinci


class Bunker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rules = f'{choice(THREAT)}. Ты стоишь вместе с другими у входа в бункер.' \
                     'Там есть все что требуется для выживания, но только для 3 человек. Вас же 6.' \
                     'Вы должны решить, кто попадет в бункер, а кто нет.' \
                     'Каждый раунд каждый игрок расскрывает свою характеристику.' \
                     'В конце раунда игроки обязаны выбрать одного человека, которого следует выгнать'
        print(self.rules)
        self.bots = Bots(api_key=api_key, bots_name=['Даня', 'Илья', 'Катя', 'Макс', 'Ваня', 'Адам'], rules=self.rules)

        self.chat_gpt = ChatGPT(api_key)
        self.text_davinci = TextDavinci(api_key)
        self.choice = 1

    def start_game(self):
        for i in range(0, 3):
            self.bots.bots_discussion(i == 0)
            while True:
                self.bots.bots_solution()
                if self.bots.leave():
                    break
        print('Сервер: В бункер попали:')
        for bot in self.bots.bots:
            print(f'   -{bot["name"]}')
        print('Конец игры')
