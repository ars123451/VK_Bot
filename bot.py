import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging

try:
    import settings
except ImportError:
    exit('Do copy settings.py.default and set token!!!')

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s '))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename='bot.log', mode='w', encoding='UTF8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s  -  %(levelname)s  -  %(message)s', "%Y-%m-%d %H:%M"))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    """
    Echo bot for Vk.com.
    Use Python 3.11.3
    """

    def __init__(self, token, group_id):
        """

        :param token: secret token from vk group
        :param group_id: group id from vk group
        """
        self.token = token
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """ Run bot """
        for event in self.long_poller.listen():
            try:
                self.on_event(event=event)
            except Exception as exc:
                log.exception(f'===***{exc}***===')

    def on_event(self, event):
        """
        Return your message if it is a text

        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.info(event.object['message']['text'])
            self.api.messages.send(
                message=event.object['message']['text'],
                random_id=time.time(),
                peer_id=event.object['message']['peer_id'])
        else:
            log.debug(("We cann't handle this type of event", event.type))


if __name__ == '__main__':
    configure_logging()
    bot = Bot(token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
