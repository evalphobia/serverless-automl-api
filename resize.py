from PIL import Image
from io import BytesIO

_1MB = 1024*1024


def resize(byt):
    if _is_big_size(byt):
        return _resize(byt)
    return byt


def _resize(byt):
    img = Image.open(BytesIO(byt))
    img.thumbnail((600, 600), Image.NEAREST)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    result = BytesIO()
    img.save(result, format='JPEG')
    return result.getvalue()


def _is_big_size(byt):
    return len(byt) > _1MB
