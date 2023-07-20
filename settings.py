TOKEN = 'vk1.a.iD9lvBPjTVFv1C0Qz8gt72Z2m8ff8AamuSaizA80gHIpViAWrDjwNUhbIthl5y7VB1QOPcb5mUB' \
        'T8S-pNpD2sjp-nTRWIVSHwTB7lSe61Rf4MIcgoMTRGafluCnz-uvfi7rz00OmnmPC1Yq0_LFpQcd115a5' \
        '3I26weTpW_FiyI-csI0pBrxnXSuH34vdjDmX888RPLce00oVqPJKr3Ds6g'

GROUP_ID = 220981746

INTENTS = [
    {
        "name": "Дата проведения",
        "tokens": ("когда", "сколько", "дату", "дата"),
        "scenario": None,
        "answer": "Конференция проводится 19 февраля. Регистрация начинается в 10:00"
    },
    {
        "name": "Место проведения ",
        "tokens": ("где", "место", "адрес", "метро"),
        "scenario": None,
        "answer": "Конференция пройдёт в городе Москва"
    },
    {
        "name": "Регистрация",
        "tokens": ("регистр", "добав"),
        "scenario": "registration",
        "answer": None
    }
]
SCENARIOS = {
    'registration': {
        "first_step": "step_1",
        "steps": {
            "step_1": {
                "text": "Чтобы зарегистрироваться, введите своё имя:",
                "failure_text": "Имя должно состоять из 3-30 букв и дефиса. Введите имя ещё раз!",
                "handler": "handle_name",
                "next_step": "step_2"
            },
            "step_2": {
                "text": "Введите email. На него придёт вся информация",
                "failure_text": "Некорректный email. Введите email ещё раз!",
                "handler": "handle_email",
                "next_step": "step_3"
            },
            "step_3": {
                "text": "Спасибо за регистрацию, {name}! Мы пришлём билет на {email}. Распечатайте его",
                "image": "handle_generate_ticket",
                "failure_text": None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

DEFAULT_ANSWER = "Не знаю как на это ответить, спросите что-то другое ! "

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='1234',
    host='localhost',
    database='vk_chat_bot'
)
