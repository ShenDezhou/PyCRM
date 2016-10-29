#-*- coding=utf-8 -*-
__author__ = 'wangjinlong@asiencredit.com'

from __init__ import *
import os
import random
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageOps
import StringIO
import re
import qrcode


NON_DIGITS_RX = re.compile('[^\d]')
try:
    PIL_VERSION = int(NON_DIGITS_RX.sub('', Image.VERSION))
except:
    PIL_VERSION = 116

# Distance of the drawn text from the top of the captcha image
from_top = 10

colors = [(250, 125, 30), (15, 65, 150), (210, 30, 90), (64, 25, 90), (10, 120, 40), (95, 0, 16)]


def noise_arcs(draw, image):
    size = image.size
    draw.arc([-20, -20, size[0], 20], 0, 295, fill=random.choice(colors))
    draw.line([-20, 20, size[0] + 20, size[1] - 20], fill=random.choice(colors))
    draw.line([-20, 0, size[0] + 20, size[1]], fill=random.choice(colors))
    return draw


def noise_dots(draw, image):
    size = image.size
    for p in range(int(size[0] * size[1] * 0.1)):
        draw.point((random.randint(0, size[0]), random.randint(0, size[1])), fill=random.choice(colors))
    return draw


def post_smooth(image):
    try:
        import ImageFilter
    except ImportError:
        from PIL import ImageFilter
    return image.filter(ImageFilter.SMOOTH)


def random_chars(length):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ret = ''
    for i in range(length):
        ret += random.choice(chars)
    return ret


def getsize(font, text):
    if hasattr(font, 'getoffset'):
        return [x + y for x, y in zip(font.getsize(text), font.getoffset(text))]
    else:
        return font.getsize(text)


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def recaptcha(text, scale=1):

    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts/Vera.ttf'), 22*scale)
    size = getsize(font, text)
    size = (size[0] * 2, int(size[1] * 1.4))

    image = Image.new('RGB', size, color=(255, 255, 255))
    xpos = 2

    for i, char in enumerate(text):

        fgimage = Image.new('RGB', size, '#001100')
        charimage = Image.new('L', getsize(font, ' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if PIL_VERSION >= 116:
            charimage = charimage.rotate(random.randrange(-35, 35, 5), expand=0, resample=Image.BICUBIC)
        else:
            charimage = charimage.rotate(random.randrange(-35, 35, 5), resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)
        maskimage.paste(charimage, (xpos, from_top, xpos + charimage.size[0], from_top + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 10 + charimage.size[0]

    #image = image.crop((0, 0, xpos + 1, size[1]))

    draw = ImageDraw.Draw(image)
    draw = noise_arcs(draw, image)
    draw = noise_dots(draw, image)
    image = post_smooth(image)
    #image = reduce_opacity(image, 0.5)

    del draw
    strio = StringIO.StringIO()
    image.save(strio, 'PNG')
    strio.seek(0)
    return strio


def getcaptcha(length = 4):
    """获取验证码
    """
    capstr = random_chars(length)
    return recaptcha(capstr, 1), capstr

# def get_qrcode(url):
#     qr = qrcode.QRCode(
#         version=2,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=1
#     )
#     qr.add_data(url)
#     qr.make(fit=True)
#     img = qr.make_image()
#     strio = StringIO.StringIO()
#     img.save(strio, 'PNG')
#     strio.seek(0)
#     return strio

def get_qrcode(url,icon_url=None):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    if icon_url and is_file_existed(icon_url):
        width = img.pixel_size
        img = img.convert("RGB")
        icon = Image.open(get_file_path(icon_url))
        icon.thumbnail((int(width*0.2), int(width*0.2)), resample=1)
        iconwidth = icon.size[0]
        box=(int(width-iconwidth)/2,int(width-iconwidth)/2,int(width-iconwidth)/2 + iconwidth,int(width-iconwidth)/2 + iconwidth)
        img.paste(icon,box)
    strio = StringIO.StringIO()
    img.save(strio, 'PNG')
    strio.seek(0)
    return strio