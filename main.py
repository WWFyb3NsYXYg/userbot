from __future__ import print_function

from telethon import TelegramClient, events, types, utils
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, User

import time

import speech
import os
import sys
import helpers
import asyncio
import datetime
import random

import khaleesi

api_id = 'TELETHON_API_ID'
api_hash = 'TELETHON_API_HASH'

client = TelegramClient('USERBOT', api_id, api_hash)
client.start()


#help
@client.on(events.NewMessage(pattern='^!h$', outgoing=True))
async def help(event: events.NewMessage.Event):
    reply_text = f'**Userbot help** \n\n' \
        '`scan [ответ на сообщение]` - сканировать сообщение,\n' \
        '`scans [ответ на сообщение]` - молча сканировать сообщение,\n' \
        '`gum [ответ на сообщение]` - вставить смайлики посреди сообщения,\n' \
        '`cum [ответ на сообщение]` - кхалиси сообщение,\n' \
        '`tr [ответ на сообщение]` - перевод сообщения,\n' \
        '`trl {текст или [ответ на сообщение]}` - перевод на latin,\n' \
        '`!w` - погода,\n' \
        '`!s {запрос }` - поиск в Google,\n' \
        '`!t` - имитация печатания в течение 5 минут,\n' \
        '`ot` - случайная "отмазка",\n' \
        '`year` - информация о годе,\n' \
        '`covg` - информация о ковидной диаграмме,\n' \
        '`sat` - изображение со спутника,\n' \
        '`!m {20} {m/h/d}` - заглушить пользователя на {20} {m} минут,\n' \
        '`🦔` - классный "мультик",\n' \
        '`loading` - анимация загрузки,\n' \
        '`!f {text}` - анимация текста,\n' \
        '`!a {text or [ответ на сообщение]}` - текст в голосовое сообщение,\n' \
        '`!v {text or [ответ на сообщение]}` - текст в видио сообщение,\n' \
        '`!d {text or [ответ на сообщение]}` - текст в голосовое сообщение с фильтром демон,\n' \
        '`btc` - курс биткойна.'

    await event.edit(reply_text)


#userId
@client.on(events.NewMessage(pattern='^scans$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    reply_text = await helpers.build_user_info(event)
    await client.send_message('me', reply_text)
    await event.delete()


#chatid
@client.on(events.NewMessage(pattern='^scan$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    reply_text = await helpers.build_user_info(event)
    await event.edit(reply_text)


#break message
@client.on(events.NewMessage(pattern='^gum$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    if event.message.is_reply:
        msg = await event.message.get_reply_message()
        reply_text = helpers.break_text(msg.text)
        await event.edit(reply_text)


#khaleesi message
@client.on(events.NewMessage(pattern='^cum$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    if event.message.is_reply:
        msg = await event.message.get_reply_message()
        reply_text = khaleesi.Khaleesi.khaleesi(msg.text)
        await event.edit(reply_text)


#translate message
@client.on(events.NewMessage(pattern='^tr$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    if event.message.is_reply:
        msg = await event.message.get_reply_message()
        await event.edit('Translating...')
        reply_text = helpers.translate_text(msg.message)
        await event.edit(reply_text)


#translate message latin
@client.on(events.NewMessage(pattern='^trl', outgoing=True))
async def handler(event: events.NewMessage.Event):
    msg_text = (await event.message.get_reply_message()).text if event.message.is_reply else event.message.text.replace('trl', '').strip()
    await event.edit('👹')
    reply_text = helpers.translate_text(msg_text, dest='la', silent_mode=True)
    await event.edit(reply_text)


#search text
@client.on(events.NewMessage(pattern='^!s', outgoing=True))
async def handler(event: events.NewMessage.Event):
    origin_text = event.message.text.replace('!s', '').strip()
    await event.edit('Поиск...')
    reply_text = helpers.google_search(origin_text)
    await event.edit(reply_text, link_preview = True)


#send typing
@client.on(events.NewMessage(pattern='^!t$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.delete()
        async with client.action(chat, 'typing'):
            await asyncio.sleep(300)
            pass

    except Exception as e:
        print(e)


#weather
@client.on(events.NewMessage(pattern='^!w$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    weather = helpers.get_weather()
    await event.edit(weather)


#otmazka
@client.on(events.NewMessage(pattern='^ot$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        otm = helpers.random_otmazka()
        await event.edit(otm)

    except Exception as e:
        print(e)


#year progress
@client.on(events.NewMessage(pattern='^year$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        text = "Год:\n"
        text += helpers.get_year_progress(30)
        await event.edit(f'`{text}`')

    except Exception as e:
        print(e)


#covid
@client.on(events.NewMessage(pattern='^covg$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.edit("Загрузка...")
        img_name = helpers.covid_graph()
        await event.delete()
        cov = helpers.get_covid()
        await client.send_file(chat, img_name, caption=cov)

    except Exception as e:
        print(e)


#satelite image
@client.on(events.NewMessage(pattern='^sat$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.edit("Загрузка...")
        img_name = helpers.get_sat_img()
        await event.delete()
        await client.send_file(chat, img_name)

    except Exception as e:
        print(e)


#autoresponder
@client.on(events.NewMessage(incoming=True))
async def handler(event: events.NewMessage.Event):
    chat = event.chat if event.chat else (await event.get_chat()) # telegram MAY not send the chat enity

    if event.is_private:
        if event.voice:
            reply_text = 'Голосовое сообщение не доставлено так как пользователь заблокировал эту опцию.'
            await client.send_message(chat, reply_text, reply_to = event.message.id)

    if event.is_group:
        try:
            msg = event.message
            chat_title = chat.title.replace(' ', '\ ').replace('=', '\=')
            
            user_name = ''
            if msg.sender.username:
                user_name += '@' + msg.sender.username
                
            try:
                if msg.sender.first_name:
                    user_name += f' {msg.sender.first_name}'
                if msg.sender.last_name:
                    user_name += f' {msg.sender.last_name}'
            except:
                user_name = f' {msg.sender.title}'

            user_name = user_name.replace(' ', '\ ').replace('=', '\=')

            chat_id = chat.id
            user_id = msg.sender.id
            sender: User = await event.get_sender()

            #print(f'bots,botname=kodzuthon,chatname={chat_title},chat_id={chat_id},user_id={user_id},user_name={user_name} imcome_messages=1')
        except:
            pass

#mute user
@client.on(events.NewMessage(pattern=r'^!m', outgoing=True))
async def handler(event: events.NewMessage.Event):
    chat = await event.get_chat()
    reply_to_message = await event.get_reply_message()

    if not reply_to_message:
        await event.delete()
        return

    time_flags_dict = {
        "m": [60, "минут"],
        "h": [3600, "часов"],
        "d": [86400, "дней"]
        }

    try:
        #m or h or d
        time_type = event.message.text[-1]

        #get number
        count = int(event.message.text.split()[1][:-1])

        #convert to seconds
        count_seconds = count * time_flags_dict[time_type][0]

        rights = ChatBannedRights(
            until_date=datetime.datetime.utcnow() + datetime.timedelta(seconds=count_seconds),
            send_messages=True
        )

        await client(EditBannedRequest(chat.id, reply_to_message.sender_id, rights))
        await event.edit(f'Заглушен на {count} {time_flags_dict[time_type][1]}')

    except Exception as e:
        print(e)


#🦔🍎
@client.on(events.NewMessage(pattern='^🦔$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    for i in range(19):
        await event.edit('🍎'*(18 - i) + '🦔')
        await asyncio.sleep(.5)


#Loading
@client.on(events.NewMessage(pattern='^loading$', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        percentage = 0
        while percentage < 100:
            temp = 100 - percentage
            temp = temp if temp > 5 else 5
            percentage += temp / random.randint(5, 10)
            percentage = round(percentage, 2)
            # if percentage > 100: percentage = 100
            progress = int(percentage // 5)
            await event.edit(f'`|{"█" * progress}{"-" * (20 - progress)}| {percentage}%`')
            await asyncio.sleep(.5)

        time.sleep(5)
        await event.delete()

    except Exception as e:
        print(e)


#print citate
@client.on(events.NewMessage(pattern='^!f', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        origin_text = event.message.text.replace('!f ', '')
        for i in range(len(origin_text)):
            if origin_text[i] == " ": continue
            await event.edit(origin_text[:i+1])
            await asyncio.sleep(.1)

    except Exception as e:
        print(e)


#voice note
@client.on(events.NewMessage(pattern='^!a', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.delete()
        async with client.action(chat, 'record-voice'):
            origin_text = event.message.text.replace('!a', '').strip()

            if event.message.is_reply and origin_text == '':
                msg = await event.message.get_reply_message()
                origin_text = msg.text

            voicename, _duration = speech.syntese(origin_text, background = False)

            chat = await event.get_chat()
            wafe_form = speech.get_waveform(0, 31, 100)
            await client.send_file(chat, voicename, reply_to = event.message.reply_to_msg_id, attributes=[types.DocumentAttributeAudio(duration=_duration, voice=True, waveform=utils.encode_waveform(bytes(wafe_form)))]) # 2**5 because 5-bit

            speech.try_delete(voicename)

    except Exception as e:
        print(e)


#video note
@client.on(events.NewMessage(pattern='^!v', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.delete()
        async with client.action(chat, 'record-round'):
            # make sound
            origin_text = event.message.text.replace('!v ', '')
            voicename, _duration = speech.syntese(origin_text, background = False)

            # mount to video
            video_file = speech.mount_video(voicename)

            chat = await event.get_chat()
            await client.send_file(chat, video_file, reply_to = event.message.reply_to_msg_id, video_note=True)

            speech.try_delete(voicename)
            speech.try_delete(video_file)

    except Exception as e:
        print(e)


#demon voice note
@client.on(events.NewMessage(pattern='^!d', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        chat = await event.get_chat()
        await event.delete()
        async with client.action(chat, 'record-voice'):
            origin_text = event.message.text.replace('!d ', '')
            voicename, _duration = speech.demon(origin_text)

            chat = await event.get_chat()
            wafe_form = speech.get_waveform(0, 31, 100)
            await client.send_file(chat, voicename, reply_to = event.message.reply_to_msg_id, attributes=[types.DocumentAttributeAudio(duration=_duration, voice=True, waveform=utils.encode_waveform(bytes(wafe_form)))]) # 2**5 because 5-bit

            speech.try_delete(voicename)

    except Exception as e:
        print(e)

#btc price
@client.on(events.NewMessage(pattern='(^btc$)|(^Btc$)|(^BTC$)', outgoing=True))
async def handler(event: events.NewMessage.Event):
    try:
        btc_price = helpers.get_btc()
        await event.edit(btc_price)

    except Exception as e:
        print(e)

#update bio
async def update_bio():
    while True:
        new_about = helpers.get_year_progress()
        print(f'Обновление bio {new_about}')
        await client(UpdateProfileRequest(about=new_about))
        await asyncio.sleep(300)

        # https://github.com/gawel/aiocron CRON <====================================


try:
    print('(Успешно запущено)')
    print('(Нажмите Ctrl+C для остановки)')
    loop = asyncio.get_event_loop()
    task = loop.create_task(update_bio())
    loop.run_until_complete(task)
    client.run_until_disconnected()
finally:
    client.disconnect()