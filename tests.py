from unittest import TestCase
from unittest.mock import patch, Mock, ANY
import time

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType

from bot import Bot


class Test1(TestCase):
    RAW_EVENT = {'group_id': 220981746,
                 'type': 'message_new',
                 'event_id': '9e5b49abee314661461f8ada90c8d8d42628f9de',
                 'v': '5.131',
                 'object':
                     {'message':
                          {'date': 1687042390,
                           'from_id': 532090271,
                           'id': 287,
                           'out': 0,
                           'attachments': [],
                           'conversation_message_id': 214,
                           'fwd_messages': [],
                           'important': False,
                           'is_hidden': False,
                           'peer_id': 532090271,
                           'random_id': 0,
                           'text': 'Привет!'},
                      'client_info':
                          {'button_actions': ['text', 'vkpay', 'open_app', 'location',
                                              'open_link', 'open_photo', 'callback',
                                              'intent_subscribe', 'intent_unsubscribe'],
                           'keyboard': True,
                           'inline_keyboard': True,
                           'carousel': True,
                           'lang_id': 0}
                      }
                 }

    def test_run(self):
        count = 5
        obj = {}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)

        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                # bot.on_event.assert_any_call({})
                assert bot.on_event.call_count == count

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll'):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.message.send = send_mock

                bot.on_event(event)

                # send_mock.assert_called_once_with(
                #     message=self.RAW_EVENT['object']['message']['text'],
                #     random_id=ANY,
                #     peer_id=self.RAW_EVENT['object']['message']['peer_id']
                # )
