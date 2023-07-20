import time

import requests
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import handlers
from models import UserState, Registration

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


# class UserState:
#     def __init__(self, scenario_name, step_name, context=None):
#         self.scenario_name = scenario_name
#         self.step_name = step_name
#         self.context = context or {}


class Bot:
    """
    Echo bot for Vk.com.
    Use Python 3.11.3


    -ask name
    -ask email
    -says if the registration is correct

    repeat if this step not ready
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

    @db_session
    def on_event(self, event):
        """
        Return your message if it is a text

        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug(("We can't handle this type of event", event.type))
            return

        user_id = event.object.message['peer_id']
        text = event.object.message['text'].lower()
        state = UserState.get(user_id=str(user_id))
        if state is not None:
            self.continue_scenario(text=text, state=state, user_id=user_id)
        else:
            # search intent
            for intent in settings.INTENTS:
                # log.debug(f'We get {intent}')
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id=user_id, scenario_name=intent['scenario'], text=text)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=time.time(),
            peer_id=user_id
        )

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachment,
            random_id=time.time(),
            peer_id=user_id
        )

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handle = getattr(handlers, step['image'])
            image = handle(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)

            if next_step['next_step']:
                # switch to next sgtep
                state.step_name = step['next_step']
            else:
                log.info('{name} {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            # retry this step
            self.send_text(step['failure_text'], user_id)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
