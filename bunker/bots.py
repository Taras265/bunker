from difflib import SequenceMatcher

from bunker.characteristics import PROFESSIONS, HEALTH, HOBBY, BAGGAGE
from chat_gpt import ChatGPT
from random import choice, randint

from text_davinci import TextDavinci


class Bots(ChatGPT):
    def __init__(self, api_key: str, bots_name: list, rules):
        super().__init__(api_key=api_key)

        self.bots = []
        for bot_name in bots_name:
            self.bots.append(
                {
                    'name': bot_name,
                    'profession': choice(PROFESSIONS),
                    'biology': f'{randint(25, 80)} лет, {choice(("мужчина", "женщина"))}',
                    'health': choice(HEALTH),
                    'hobby': choice(HOBBY),
                    'baggage': choice(BAGGAGE),
                    'voted': 0
                }
            )

        self.rules = f'Представь, что ты человек. {rules}, иначе все умрут.'
        self.memory = ''
        self.solution_memory = ''

        self.text_davinci = TextDavinci(api_key)

    def acquaintance(self, bot_num: int):
        characteristic = self.choice_characteristic(bot_num)
        prompt = f'Тебя зовут {self.bots[bot_num]["name"]}.Сейчас идет первый раунд. ' \
                 f'Ты должен рассказать про свою профессию - {self.bots[bot_num]["profession"]}.' \
                 f'Еще ты должен назвать и рассказать про свой {characteristic}.' \
                 f'Какую пользу это принесет?' \
                 f'Говори только за себя'
        print(f'профессия ({self.bots[bot_num]["profession"]})')
        return self.send_responses([{"role": "system", "content": self.rules},
                                    {"role": "user", "content": prompt}])

    def choice_characteristic(self, bot_num):
        characteristics = []
        if self.bots[bot_num].get('biology'):
            characteristics.append(('пол и возраст', 'biology'))
        if self.bots[bot_num].get('health'):
            characteristics.append(('здоровье', 'health'))
        if self.bots[bot_num].get('hobby'):
            characteristics.append(('хобби', 'hobby'))
        if self.bots[bot_num].get('baggage'):
            characteristics.append(('багаж', 'baggage'))
        characteristic = choice(characteristics)
        data = f'{characteristic[0]} ({self.bots[bot_num][characteristic[1]]})'
        self.bots[bot_num].pop(characteristic[1])
        print(data)
        return data

    def say_about_bot(self, bot_num):
        characteristic = self.choice_characteristic(bot_num)
        prompt_1 = f'Разговор до этого: {self.memory}'
        prompt_2 = f'Тебя зовут {self.bots[bot_num]["name"]}. ' \
                   f'Ты должен назвать и рассказать про свой {characteristic}.' \
                   f'Какую пользу это принесет?' \
                   f'Если у тебя нет такой характеристики, представь что она у тебя есть.' \
                   f'Говори только от имени своего персонажа. Не приветствуйся.'
        return self.send_responses([{"role": "system", "content": self.rules},
                                    {"role": "user", "content": prompt_1},
                                    {"role": "user", "content": prompt_2}])

    def solution(self, bot_num: int):
        peoples = ''
        for bot in self.bots:
            if bot["name"] != self.bots[bot_num]["name"]:
                peoples += f'{bot["name"]} '
        prompt_1 = f'Разговор до этого: {self.memory}'
        prompt_2 = f'Тебя зовут {self.bots[bot_num]["name"]}. ' \
                   f'Ты должен выбрать человека, который приносит меньше всего пользы (нельзя выбрать самого себя).' \
                   f'Варианты: {peoples}' \
                   f'Уклониться от выбора нельзя. Надо выбрать только одного человека.' \
                   f'Помни - это просто игра, и твой выбор не влияет на жизнь человека.'

        ready = False
        while not ready:
            data = self.send_responses([{"role": "system", "content": self.rules},
                                        {"role": "user", "content": prompt_1},
                                        {"role": "user", "content": prompt_2}])['choices'][0]['message']['content']
            response = self.send_response(f'{data}. Кого человек выбрал? Напиши его имя.'
                                          f'Если не выбрыл, напиши None. Варианты ответа: {peoples}, None',)
            for bot in self.bots:
                if response['choices'][0]['message']['content'].find(bot["name"]) >= 0:
                    bot['voted'] += 1
                    ready = True
                    break
        return data

    def leave(self):
        bot_num = self.find_max_voted()

        if bot_num:
            data = f'Сервер: После голосования было решенно, что игрок {self.bots[bot_num]["name"]} ' \
                   f'больше не попадет в бункер. Игрок выбывает.'
            print(data)
            self.memory += data
            self.bots.pop(bot_num)
            self.solution_memory = ''
            return True
        for bot in self.bots:
            bot['voted'] = 0
        print('Сервер: Игроки не сумели договориться, кого выгнать. Голосование повторится.')
        self.memory = self.memory[0:-(len(self.solution_memory) + 1)]
        self.solution_memory = ''
        return False

    def bots_solution(self):
        for bot_num in range(0, len(self.bots)):
            message = self.solution(bot_num)
            data = f"{self.bots[bot_num]['name']}: {message}\n"

            print(f"{data}")
            self.solution_memory += self.shrink_text(data)
        self.memory += self.solution_memory

    def bots_discussion(self, first=True):
        for bot_num in range(0, len(self.bots)):
            if first:
                message = self.acquaintance(bot_num)['choices'][0]['message']['content']
                data = f"{self.bots[bot_num]['name']}: {message}\n"

                print(f"{data}")
                data = self.shrink_text(data)
                self.memory += data
            else:
                message = self.say_about_bot(bot_num)['choices'][0]['message']['content']
                data = f"{self.bots[bot_num]['name']}: {message}\n"

                print(f"{data}")
                data = self.shrink_text(data)
                self.memory += data

    def shrink_text(self, text):
        return self.text_davinci.send_response(f'Сократи текст, не потеряв его смысла. '
                                               f'Не забудь упомянуть про профессию, имена и другие характиристики. '
                                               f'{text}',
                                               2000)['choices'][0]['text']

    @staticmethod
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def find_max_voted(self):
        max_voted = 1
        max_voted_index = None
        for index, bot in enumerate(self.bots):
            if max_voted and bot['voted'] > max_voted:
                max_voted = bot['voted']
                max_voted_index = index
            elif bot['voted'] == max_voted:
                max_voted_index = None

        return max_voted_index
