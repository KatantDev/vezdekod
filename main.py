import logging
import sqlite3
import os

from random import choice
from uuid import uuid4

import aiofiles
import aiohttp
from vkbottle import Keyboard, Callback, Text, Location, OpenLink, VKPay, KeyboardButtonColor, BaseStateGroup, \
    ShowSnackbarEvent
from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle.dispatch.rules.base import AttachmentTypeRule
from vkbottle.tools import PhotoMessageUploader
from vkbottle_types.events import GroupEventType

bot = Bot('f0f3a22ec2abe93c03ec507b6f5f8f1068ba01c12879b42ffd64981f9fb5c0125f6659c2d7e3f9a854c19')
logging.basicConfig(level=logging.INFO)

con = sqlite3.connect('vezdekod.db')
cur2 = con.cursor()
con.row_factory = lambda cursor, row: row[0]
cur = con.cursor()


class States(BaseStateGroup):
    Question1 = 0
    Question2 = 1
    Question3 = 2
    Question4 = 3
    Question5 = 4
    Question6 = 5
    Question7 = 6
    Question8 = 7
    LoadMeme = 8


@bot.on.private_message(text='Привет')
async def handler(message: Message):
    question = Keyboard(inline=True)
    question.add(Callback('Да, конечно', {"cmd": "yes"}), color=KeyboardButtonColor.POSITIVE)

    await message.answer(
        'Привет вездекодерам! Могу ли я задать вам несколько вопросов?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question1)


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent,
                  func=lambda event: event.object.payload['cmd'] == 'yes')
async def _(event: MessageEvent):
    question = Keyboard(inline=True)
    question.add(Text('Отлично'), color=KeyboardButtonColor.NEGATIVE)
    question.add(Text('Так себе :('), color=KeyboardButtonColor.PRIMARY)
    question.row()
    question.add(Text('Могло быть и лучше'), color=KeyboardButtonColor.SECONDARY)

    await event.send_message(
        message='Как твои дела?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(event.peer_id, States.Question2)


@bot.on.private_message(text=['Отлично', 'Так себе :(', 'Могло быть и лучше'], state=States.Question2)
async def _(message: Message):
    question = Keyboard(one_time=True, inline=False)
    question.add(Location({'cmd': 'send_location'}), color=KeyboardButtonColor.NEGATIVE)
    question.row()
    question.add(Text('Я доеду сам(а)'), color=KeyboardButtonColor.SECONDARY)
    await message.answer(
        'Предлагаю съездить сегодня в кино, я вызову тебе такси. Подскажи, где ты живёшь?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question3)


@bot.on.private_message(func=lambda message: message.geo, state=States.Question3)
@bot.on.private_message(text='Я доеду сам(а)', state=States.Question3)
async def _(message: Message):
    question = Keyboard(one_time=True, inline=False)
    question.add(OpenLink('https://afisha.yandex.ru/moscow/cinema/brat-1997', 'Брат (Mori Cinema)'))
    question.add(Text('Мне нравится, идём!'), color=KeyboardButtonColor.SECONDARY)

    await message.answer(
        'Я уже выбрал кино, поэтому переходи по ссылке чтобы узнать на что мы идем.\nКак тебе?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question4)


@bot.on.private_message(text='Мне нравится, идём!', state=States.Question4)
async def _(message: Message):
    question = Keyboard(inline=True)
    question.add(VKPay(hash='action=transfer-to-group&group_id=212552911'))
    question.row()
    question.add(Text('Перевел(а)!'), color=KeyboardButtonColor.POSITIVE)
    question.add(Text('Я оплачу сам(а)'), color=KeyboardButtonColor.NEGATIVE)

    await message.answer(
        'Я прямо сейчас беру билеты. Переведешь 250 рублей?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question5)


@bot.on.private_message(text=['Перевел(а)!', 'Я оплачу сам(а)'], state=States.Question5)
async def _(message: Message):
    question = Keyboard(one_time=True, inline=False)
    question.add(Text('Отлично'), color=KeyboardButtonColor.POSITIVE)
    question.add(Text('Так себе'), color=KeyboardButtonColor.NEGATIVE)

    await message.answer(
        'Отлично, а теперь хотелось бы узнать, как ты относишься к мемам?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question6)


@bot.on.private_message(text=['Отлично', 'Так себе'], state=States.Question6)
async def _(message: Message):
    question = Keyboard(inline=True)
    question.add(Text('Да, конечно'), color=KeyboardButtonColor.POSITIVE)

    await message.answer(
        'У меня есть штука, которая поможет тебе их полюбить, посмотришь?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question7)


@bot.on.private_message(text='Да, конечно', state=States.Question7)
async def _(message: Message):
    question = Keyboard(inline=True)
    question.add(Text('Точно!'), color=KeyboardButtonColor.SECONDARY)

    await message.answer(
        'Ты точно готов?',
        keyboard=question.get_json()
    )
    await bot.state_dispenser.set(message.peer_id, States.Question8)


@bot.on.private_message(text='Меню')
@bot.on.private_message(text='Точно!', state=States.Question8)
async def _(message: Message):
    question = Keyboard(inline=False)
    question.add(Text('Мем'), color=KeyboardButtonColor.POSITIVE)
    question.add(Text('Статистика'), color=KeyboardButtonColor.POSITIVE)
    question.row()
    question.add(Text('Топ-9 Мемов'), color=KeyboardButtonColor.SECONDARY)
    question.add(Text('Загрузить мем'), color=KeyboardButtonColor.SECONDARY)

    await message.answer(
        'Теперь тебе доступно меню для управления. Что будем использовать?',
        keyboard=question.get_json()
    )

    try:
        await bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass


@bot.on.private_message(text='Мем')
async def _(message: Message):
    all_photos = os.listdir('./photos/')
    rated_photos = cur.execute('SELECT photo_id FROM memes WHERE user_id=?', (message.peer_id,)).fetchall()
    photos = list(set(all_photos) ^ set(rated_photos))
    print(photos)
    if len(photos) == 0:
        await message.answer('К сожалению, мемы для оценки закончились ;(')
        return
    file = choice(list(set(all_photos) ^ set(rated_photos)))

    uploader = PhotoMessageUploader(bot.api, generate_attachment_strings=True)
    attachment = await uploader.upload(file_source=f'./photos/{file}')
    print(attachment)

    rate = Keyboard(inline=True)
    rate.add(Callback('Лайк 👍🏻', {'cmd': 'like', 'file': file, 'photo': attachment}),
             color=KeyboardButtonColor.POSITIVE)
    rate.add(Callback('Дизлайк 👎🏻', {'cmd': 'dislike', 'file': file, 'photo': attachment}),
             color=KeyboardButtonColor.NEGATIVE)
    await message.answer(attachment=attachment, keyboard=rate.get_json())


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent,
                  func=lambda event: event.object.payload['cmd'] == 'like' or event.object.payload['cmd'] == 'dislike')
async def _(event: MessageEvent):
    cur.execute('SELECT photo_id FROM memes WHERE user_id=? AND photo_id=?',
                (event.peer_id, event.object.payload['file']))
    resp = cur.fetchone()
    print(resp)
    if resp is None:
        cur.execute('INSERT INTO memes VALUES (?, ?, ?)', (event.object.payload['file'], event.peer_id,
                                                           event.object.payload['cmd']))
        con.commit()

        await event.send_message_event_answer(event_data=ShowSnackbarEvent(text='Спасибо за оценку!'))
    else:
        await event.send_message_event_answer(event_data=ShowSnackbarEvent(text='Вы уже оценили этот мем!'))


@bot.on.private_message(text='Статистика')
async def _(message: Message):
    cur.execute('SELECT photo_id FROM memes WHERE user_id=? AND types=?', (message.peer_id, 'like'))
    my_likes = len(cur.fetchall())
    cur.execute('SELECT photo_id FROM memes WHERE user_id=? AND types=?', (message.peer_id, 'dislike'))
    my_dislikes = len(cur.fetchall())

    cur.execute('SELECT photo_id FROM memes WHERE types=?', ('like',))
    all_likes = len(cur.fetchall())
    cur.execute('SELECT photo_id FROM memes WHERE types=?', ('dislike',))
    all_dislikes = len(cur.fetchall())
    await message.answer('👻 Ваша статистика:\n'
                         f'Количество пролайканных мемов: {my_likes} фото\n'
                         f'Количество задизлайканных мемов: {my_dislikes} фото\n\n'
                         f'😨 Общая статистика:\n'
                         f'Поставлено лайков: {all_likes}\n'
                         f'Поставлено дизлайков: {all_dislikes}')


@bot.on.private_message(text='Топ-9 Мемов')
async def _(message: Message):
    top = cur2.execute(
        'SELECT photo_id, COUNT(photo_id) '
        'FROM memes '
        'WHERE types="like" '
        'GROUP BY photo_id '
        'ORDER BY COUNT(photo_id) DESC '
        'LIMIT 9'
    ).fetchall()
    for i in range(len(top)):
        print(top[i], top[i][0])
        uploader = PhotoMessageUploader(bot.api, generate_attachment_strings=True)
        attachment = await uploader.upload(file_source=f'./photos/{top[i][0]}')

        await message.answer(
            f'🤖 Место №{i+1} (Лайков: {top[i][1]})',
            attachment=attachment
        )


@bot.on.private_message(text='Загрузить мем')
async def _(message: Message):
    await message.answer('Отправьте фотографию с мемом и его сможет оценить любой пользователь.')
    await bot.state_dispenser.set(message.peer_id, States.LoadMeme)


@bot.on.private_message(AttachmentTypeRule('photo'), state=States.LoadMeme)
async def _(message: Message):
    if len(message.get_photo_attachments()) == 1:
        async with aiohttp.ClientSession() as session:
            url = message.get_photo_attachments()[0].sizes[-5].url
            async with session.get(url) as resp:
                f = await aiofiles.open(f'./photos/{uuid4()}.jpg', mode='wb')
                await f.write(await resp.read())
                await f.close()
        await message.answer('Ваша фотография была загружена в список мемов, '
                             'теперь её сможет оценить любой пользователь.')
        await bot.state_dispenser.delete(message.peer_id)

    else:
        await message.answer('Отправьте только одну фотографию.')


bot.run_forever()
