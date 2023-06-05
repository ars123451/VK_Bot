import time
from Git.token_number import token_1 as token
import vk_api
import vk_api.bot_longpoll

group_id = 220981746


class Bot:
    def __init__(self, token, group_id):
        self.token = token
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            print("Get event!")
            try:
                self.on_event(event=event)
            except Exception as exc:
                print(f'===***{exc}***===')

    def on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            print(event.object['message']['text'])
            print(event.object.message)
            self.api.messages.send(
                message=event.object['message']['text'],
                random_id=time.time(),
                peer_id=event.object['message']['peer_id'])
        else:
            print("We cann't handle this type of event", event.type)


if __name__ == '__main__':
    bot = Bot(token=token, group_id=220981746)
    bot.run()
