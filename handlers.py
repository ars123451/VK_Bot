import re

re_name = r"^[\w\-\s]{3,30}$"
re_email = r'\b[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(re_email, text)
    if matches:
        context['email'] = matches[0]
        return True
    else:
        return False
