import time
from Git.token_number import token_1 as token
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from colorama import Fore, Back

group_id = 220981746


class Bot:
    def __init__(self, token, group_id):
        self.token = token
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            print("Get event!")
            try:
                self.on_event(event=event)
            except Exception as exc:
                print(Back.RED, f'===***{exc}***===', Back.RESET)

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event.object['message']['text'])
            print(event.object.message)
            self.api.messages.send(
                message=event.object['message']['text'],
                random_id=time.time(),
                peer_id=event.object['message']['peer_id'])
        else:
            print(Fore.BLUE, "We cann't handle this type of event", event.type, Fore.RESET)


if __name__ == '__main__':
    bot = Bot(token=token, group_id=220981746)
    bot.run()
