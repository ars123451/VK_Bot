import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def generate_ticket(name, email):
    base = Image.open('files/ticket.png').convert("RGBA")
    font = ImageFont.truetype(font="files/font.otf", size=20)
    d = ImageDraw.Draw(base)

    d.text((220, 50), name, font=font, fill=(255, 255, 0, 255))
    d.text((220, 75), email, font=font, fill=(255, 255, 0, 255))

    response = requests.get(url=f'https://i.pravatar.cc/50/{email}')
    avatar_bytes = BytesIO(response.content)
    avatar = Image.open(avatar_bytes)
    base.paste(avatar, box=(70, 50))

    temp_file = BytesIO()
    base.save("files/example-file", 'png')
    temp_file.seek(0)

    return temp_file
