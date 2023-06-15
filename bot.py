import time
from token_number import token_1 as token
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging

group_id = 220981746

log = logging.getLogger('bot')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s '))
stream_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(filename='bot.log', mode='w')
file_handler.setLevel(logging.INFO)

log.addHandler(stream_handler)
log.addHandler(file_handler)
log.setLevel(logging.DEBUG)


class Bot:
    def __init__(self, token, group_id):
        self.token = token
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event=event)
            except Exception as exc:
                log.exception(f'===***{exc}***===')

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.info(event.object['message']['text'])
            self.api.messages.send(
                message=event.object['message']['text'],
                random_id=time.time(),
                peer_id=event.object['message']['peer_id'])
        else:
            log.debug(("We cann't handle this type of event", event.type))


if __name__ == '__main__':
    bot = Bot(token=token, group_id=220981746)
    bot.run()
