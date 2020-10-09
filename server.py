import random

import numpy
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api import VkUpload


# Перечисления команд, режимов

class Server:
    def __init__(self, api_token, group_id, server_name: str = 'Empty'):
        global bd
        # Даем серверу имя
        self.server_name = server_name
        self.group_id = group_id
        # Для Long Poll
        self.vk = vk_api.VkApi(token=api_token)
        # Для использоания Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id, wait=30)
        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        # для загрузки изображений
        self.upload = VkUpload(self.vk_api)

    def send_msg(self, send_id, message, photo=0, keyboards='none'):
        '''
        Отправка сообщения через метод messages.send
        :param send_id: vk id пользователя, который получит сообщение
        :param message: содержимое отправляемого письма
        :return: None
        '''

        result = self.vk_api.messages.send(peer_id=send_id,
                                               message=message,
                                               random_id=random.randint(0, 2048),
                                               keyboard=open('keyboards/{}.json'.format(keyboards), 'r',
                                                             encoding='UTF-8').read())
        return result

    def Comander(self, event):
        '''
        Функция принимающая сообщения пользователя
        :param msg: Сообщение
        :return: Ответ пользователю, отправившему сообщение
        '''
        msg = event.object.text
        from_id = event.object.from_id
        peer_id = event.object.peer_id

        if '/help' == msg or 'Начать' == msg:
            self.send_msg(from_id, 'Если ты о чём-то переживаешь, можешь поделиться своими проблемами.')
        else:
            dog = Dog()
            self.send_msg(from_id, dog.randomWord())


    def start(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.Comander(event)

class Dog:
    words = [
        "Ауф",
        "Гав!",
        "ГAв!",
        "Гав Гав",
        "РРар",
        "Ух ах ух ах",
    ]
    def randomWord(self):
        single_random_choice = numpy.random.choice(self.words, size=1)
        return single_random_choice[0]


