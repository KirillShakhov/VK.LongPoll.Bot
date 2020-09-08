import random
import json
import os.path
import time
import httplib2
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
        # Словарь дял каждого отдельного пользователя

        bd = Content(self.server_name)
        bd.Start()

    def send_msg(self, send_id, message, photo=0, keyboards='none'):
        '''
        Отправка сообщения через метод messages.send
        :param send_id: vk id пользователя, который получит сообщение
        :param message: содержимое отправляемого письма
        :return: None
        '''
        if photo != 0:
            ''' Загрузка изображений в сообщения
            :param photos: путь к изображению(ям) или file-like объект(ы)
            :type photos: str, list
            '''
            photo = self.upload.photo_messages(photos='img/{1}/{0}'.format(photo, send_id))[0]
            photo = 'photo{}_{}'.format(photo['owner_id'], photo['id'])
        if photo == 0 or photo == '':
            result = self.vk_api.messages.send(peer_id=send_id,
                                               message=message,
                                               random_id=random.randint(0, 2048),
                                               keyboard=open('keyboards/{}.json'.format(keyboards), 'r',
                                                             encoding='UTF-8').read())
        else:
            result = self.vk_api.messages.send(peer_id=send_id,
                                               message=message,
                                               random_id=random.randint(0, 2048),
                                               keyboard=open('keyboards/{}.json'.format(keyboards), 'r',
                                                             encoding='UTF-8').read(),
                                               attachment=photo)
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
        personal = self.vk.method('users.get', {'user_id': from_id})
        mode = bd.Mode(peer_id)
        if event.object.action != None:
            if event.object.action['type'] == 'chat_invite_user':
                self.send_msg(peer_id, 'Этот пидр меня призвал: {0} {1}'.format(personal[0]['first_name'],
                                                                                personal[0]['last_name']))
                if bd.FindServer(peer_id):
                    self.send_msg(peer_id, 'У вас есть старые данные. Хотите их сохранить?(Да/Нет)')
                    bd.ChangeMode(peer_id, 'delserveransw')
                else:
                    bd.AddServer(peer_id, from_id)
                    self.send_msg(peer_id, '/admin - помощь для админа: {0} {1}'.format(personal[0]['first_name'],
                                                                                        personal[0]['last_name']))
        if bd.FindServer(peer_id) == False:
            bd.AddServer(peer_id, from_id)
            self.send_msg(peer_id,
                          'Произошла ошибка. Админ поменялся( (или нет). Хотите вернуть админку? Исключите бота и пригласите обратно')
            self.send_msg(peer_id, '/admin - помощь для админа: {0} {1}'.format(personal[0]['first_name'],
                                                                                personal[0]['last_name']))
        if mode == 'default':
            # if event.object.attachments != []:
            #    if event.object.attachments[0]['type'] == 'audio_message':
            #        return 'Фу, голосовуха'
            #    '''
            #    if event.object.from_id == 545158373:
            #        return 'Фу, Вохр', 0
            #    '''
            if 'бар' in msg and 'лусбухи' in msg:
                with open('file.txt') as file:
                    for line in file:
                        self.send_msg(peer_id, line)
                        time.sleep(2)
            if '/admin' == msg:
                if bd.FindAdmin(from_id, peer_id):
                    self.send_msg(peer_id,
                                  'У вас есть несколько команд:\n/add - добавить коамнду\n/del - удалить команду\n/list - список команд, которые вы добавили\n/adminadd - добавить админа\n/admindel - удалить админа\n/adminlist - список админов')
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/add' in msg:
                if bd.FindAdmin(from_id, peer_id):
                    try:
                        musor, name, otvet, mtype = msg.split('###')
                        name = name.lower()
                        photo = 0
                        fotvet, fphoto = bd.Find(name, peer_id)
                        if fotvet == 0:
                            if event.object.attachments != [] and event.object.attachments[0]['type'] == 'photo':
                                print('Фото есть')
                                print(event.object.attachments[0]['photo']['owner_id'])
                                for size in event.object.attachments[0]['photo']['sizes']:
                                    print(size)
                                    if size['type'] == 'r':
                                        urlrer = size['url']
                                        print(urlrer)
                                h = httplib2.Http('.cache')
                                response, content = h.request(urlrer)
                                try:
                                    os.makedirs('img/')
                                    os.makedirs('img/{}/'.format(peer_id))
                                except OSError:
                                    print('Директория существует')

                                out = open('img/{1}/{0}.jpg'.format(name, peer_id), 'wb')
                                out.write(content)
                                out.close()
                                photo = '{}.jpg'.format(name)
                            bd.Add(peer_id, name, otvet, photo, mtype)
                            self.send_msg(peer_id, 'Всё ок')
                        else:
                            self.send_msg(peer_id, 'Команда существует')
                    except:
                        self.send_msg(peer_id,
                                      'Не правильно введённая команда /add###name###otvet###type. type = 1 - если сообщение должно быть один в один с тем которое введено или 2 - если нужно сделать поиск в сообщении. Можно прикрепить картинку.')
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/adminadd' in msg:
                if bd.FindAdmin(from_id, peer_id):
                    try:
                        musor, idadmin = msg.split('###')
                        idadmin = int(idadmin)
                        if bd.FindAdmin(idadmin, peer_id):
                            self.send_msg(peer_id, 'Уже админ')
                        else:
                            bd.AddAdmin(peer_id, idadmin)
                            self.send_msg(peer_id, 'Всё ок')
                    except:
                        self.send_msg(peer_id, 'Не правильно введённая команда /adminadd###id')
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/admindel' in msg:
                if bd.FindAdmin(from_id, peer_id):
                    try:
                        musor, idadmin = msg.split('###')
                        idadmin = int(idadmin)
                        if bd.FindAdmin(idadmin, peer_id):
                            if bd.DelAdmin(peer_id, idadmin):
                                self.send_msg(peer_id, 'ОК')
                            else:
                                self.send_msg(peer_id, 'Нельзя свергать бога')
                        else:
                            self.send_msg(peer_id, 'Не является админом')
                    except:
                        self.send_msg(peer_id, 'Не правильно введённая команда /admindel###id')
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/adminlist' == msg:
                if bd.FindAdmin(from_id, peer_id):
                    self.send_msg(peer_id, bd.AdminList(peer_id))
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/list' == msg:
                if bd.FindAdmin(from_id, peer_id):
                    self.send_msg(peer_id, bd.ListComand(peer_id))
                else:
                    self.send_msg(peer_id, 'Вы не админ')
            if '/del' in msg:
                try:
                    if bd.FindAdmin(from_id, peer_id):
                        musor, otvet = msg.split('###')
                        otvet = otvet.lower()
                        fotvet, fphoto = bd.Find(otvet, peer_id)
                        if fotvet == 0:
                            self.send_msg(peer_id, 'Команды не существует')
                        else:
                            bd.DelComand(peer_id, otvet)
                            self.send_msg(peer_id, 'Успешное удаление')
                    else:
                        self.send_msg(peer_id, 'Вы не админ')
                except:
                    self.send_msg(peer_id,
                                  'Не правильно введённая команда /del###<команда котокую хотите удалить>. Например /del###hi')
            res, photo = bd.Find(msg.lower(), peer_id)
            if res != 0:
                self.send_msg(peer_id, res, photo)
        if mode == 'delserveransw':
            if bd.FindAdmin(from_id, peer_id):
                if msg.lower() == 'да':
                    ChangeMode(peer_id, 'default')
                    self.send_msg(peer_id, 'Данные сохранены')
                elif msg.lower() == 'нет':
                    bd.DelServer(peer_id)
                    bd.ChangeMode(peer_id, 'default')
                    bd.AddServer(peer_id, from_id)
                    self.send_msg(peer_id, 'Данные удалены')
                else:
                    self.send_msg(peer_id, 'да\нет?')
            else:
                self.send_msg(peer_id, 'Вы не админ')

        return 0

    def PersonalInfo(self, id):
        person = personal = Server().vk.method('users.get', {'user_id': id})
        return personal[0]['first_name'], personal[0]['last_name']

    def start(self):
        for event in self.long_poll.listen():  # Слушаем сервер
            # print(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.Comander(event)


class Content:
    def __init__(self, src='bd.json'):
        self.content_src = '{}.json'.format(src)

    def Start(self):
        if os.path.isfile(self.content_src) == 0:
            a_dict = []
            with open(self.content_src, 'w') as f:
                json.dump(a_dict, f, ensure_ascii=False, indent=4)

    def Add(self, peer_id, msg, otvet, photo=0, mtype=1):
        with open(self.content_src, 'r') as jfr:
            jf_file = json.load(jfr)
        for server in jf_file:
            if server['peer_id'] == peer_id:
                with open(self.content_src, 'w') as jf:
                    jf_target = server['msgs']
                    user_info = {'msg': msg, 'type': mtype, 'otvet': otvet, 'photo': photo}
                    jf_target.append(user_info)
                    json.dump(jf_file, jf, ensure_ascii=False, indent=4)

    def AddServer(self, peer_id, admin):
        with open(self.content_src, 'r') as jfr:
            jf_file = json.load(jfr)
        with open(self.content_src, 'w') as jf:
            jf_target = jf_file
            user_info = {'peer_id': peer_id, 'mode': 'default', 'last_msg': None, 'id_admin': [{'id': admin}],
                         'msgs': [{'msg': 'test', 'type': '1', 'otvet': 'ok', 'photo': 0}]}
            jf_target.append(user_info)
            json.dump(jf_file, jf, ensure_ascii=False, indent=4)

    def Find(self, fgff, peer_id):
        result = 0
        photo = 0
        with open(self.content_src, 'r') as f:
            data = json.load(f)
        for server in data:
            if server['peer_id'] == peer_id:
                for msg in server['msgs']:
                    if msg['type'] == '1':
                        if msg['msg'] == fgff:
                            print(msg['otvet'])
                            result = msg['otvet']
                            photo = msg['photo']
                    elif msg['type'] == '2':
                        if msg['msg'] in fgff:
                            print(msg['otvet'])
                            result = msg['otvet']
                            photo = msg['photo']
        return result, photo

    def Mode(self, peer_id):
        with open(self.content_src, 'r') as f:
            data = json.load(f)
        for server in data:
            if server['peer_id'] == peer_id:
                return server['mode']

    def ChangeMode(self, peer_id, mode):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        for server in servers:
            if server['peer_id'] == peer_id:
                server['mode'] = mode
        with open(self.content_src, 'w') as jf:
            json.dump(servers, jf, ensure_ascii=False, indent=4)

    def FindAdmin(self, idadmin, peer_id):
        result = False
        with open(self.content_src, 'r') as f:
            data = json.load(f)
        for server in data:
            if server['peer_id'] == peer_id:
                for admin in server['id_admin']:
                    if admin['id'] == idadmin:
                        print('Yes')
                        result = True
        return result

    def FindServer(self, peer_id):
        result = False
        with open(self.content_src, 'r') as f:
            data = json.load(f)
        for server in data:
            if server['peer_id'] == peer_id:
                result = True
        return result

    def DelServer(self, peer_id):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        n = 0
        for server in servers:
            if server['peer_id'] == peer_id:
                servers.pop(n)
            n += 1
        with open(self.content_src, 'w') as jf:
            json.dump(servers, jf, ensure_ascii=False, indent=4)

    def DelComand(self, peer_ids, msgn):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        m = -1
        b = -1
        for server in servers:
            m = m + 1
            if server['peer_id'] == peer_ids:
                for msg in server['msgs']:
                    b = b + 1
                    if msg['msg'] == msgn:
                        servers[m]['msgs'].pop(b)
        with open(self.content_src, 'w') as jf:
            json.dump(servers, jf, ensure_ascii=False, indent=4)

    def ListComand(self, peer_id):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        result = 'Команда - ответ (тип-(1 или 2))'
        for server in servers:
            if server['peer_id'] == peer_id:
                for msg in server['msgs']:
                    result = '{}\n{} - {} (тип-{})'.format(result, msg['msg'], msg['otvet'], msg['type'])
        return result

    def DelAdmin(self, peer_ids, deladmin):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        m = -1
        b = -1
        result = False
        for server in servers:
            m = m + 1
            if server['peer_id'] == peer_ids:
                for admin in server['id_admin']:
                    b = b + 1
                    if admin['id'] == deladmin:
                        if b != 0:
                            result = True
                            servers[m]['id_admin'].pop(b)
        with open(self.content_src, 'w') as jf:
            json.dump(servers, jf, ensure_ascii=False, indent=4)
        return result

    def AdminList(self, peer_ids):
        with open(self.content_src, 'r') as f:
            servers = json.load(f)
        result = ''
        for server in servers:
            if server['peer_id'] == peer_ids:
                for admin in server['id_admin']:
                    result = '{0}vk.com/id{1}\n'.format(result, admin['id'])
        return result

    def AddAdmin(self, peer_id, admin):
        with open(self.content_src, 'r') as jfr:
            jf_file = json.load(jfr)
        for server in jf_file:
            if server['peer_id'] == peer_id:
                with open(self.content_src, 'w') as jf:
                    jf_target = server['id_admin']
                    user_info = {'id': admin}
                    jf_target.append(user_info)
                    json.dump(jf_file, jf, ensure_ascii=False, indent=4)