import time
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
            text_to_send = self.continue_scenario(text=text, state=state)
        else:
            # search intent
            for intent in settings.INTENTS:
                # log.debug(f'We get {intent}')
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id=user_id, scenario_name=intent['scenario'])
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(
            message=text_to_send,
            random_id=time.time(),
            peer_id=user_id
        )

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})
        return text_to_send

    def continue_scenario(self, text, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next stepl
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                log.info('{name} {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            # retry this step
            text_to_send = step['failure_text']
        return text_to_send


if __name__ == '__main__':
    configure_logging()
    bot = Bot(token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
