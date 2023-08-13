import base64
import os
from typing import Union

from django.core.files.base import ContentFile


def str_to_int(value: str) -> Union[int, None]:
    if not value:
        return None
    try:
        result = int(value)
    except ValueError:
        result = None
    return result


def base64_to_image(data: str):
    format, image = data.split(';base64,')
    ext = format.split('/')[-1]
    return ContentFile(base64.b64decode(image), name='image.' + ext)


def image_to_base64(file_name: str) -> str:
    ext = os.path.splitext(file_name)[1]
    format = f'data:image/{ext[1:]};base64'
    with open(file_name, 'rb') as file:
        image = base64.b64encode(file.read()).decode()
        return f'{format},{image}'
