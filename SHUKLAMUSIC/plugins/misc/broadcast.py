# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------
import asyncio
import re
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS
from SHUKLAMUSIC.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from SHUKLAMUSIC.utils.decorators.language import language
from SHUKLAMUSIC.utils.formatters import alpha_to_int
from config import adminlist

try:
    from SHUKLAMUSIC.core.mongo import mongodb as _db
except ImportError:
    from SHUKLAMUSIC.utils.database import mongodb as _db

IS_BROADCASTING = False

# ===== "ADD ME BABY" button (on/off tumhare haath me) =====
ADD_BTN_TEXT = "ADD ME BABY"
_settings = _db.broadcast_settings


async def addbtn_is_on() -> bool:
    doc = await _settings.find_one({"_id": "addbtn"})
    return bool(doc and doc.get("on"))  # default: OFF


def add_button():
    link = (
        f"https://t.me/{app.username}?startgroup=true"
        "&admin=delete_messages+invite_users+pin_messages+manage_video_chats"
    )
    return InlineKeyboardMarkup([[InlineKeyboardButton(ADD_BTN_TEXT, url=link)]])


async def want_button(text: str) -> bool:
    """-btn  -> is broadcast me button lagao
    -nobtn -> is broadcast me button mat lagao
    kuch nahi likha -> /addbtn ki saved setting (default OFF)"""
    if re.search(r"(?<!\S)-nobtn\b", text):
        return False
    if re.search(r"(?<!\S)-btn\b", text):
        return True
    return await addbtn_is_on()


@app.on_message(filters.command("addbtn") & SUDOERS)
async def addbtn_cmd(client, message):
    arg = message.command[1].lower() if len(message.command) > 1 else "status"
    if arg in ("on", "off"):
        await _settings.update_one(
            {"_id": "addbtn"}, {"$set": {"on": arg == "on"}}, upsert=True
        )
    elif arg != "status":
        return await message.reply_text("Usage: /addbtn on | off | status")
    on = await addbtn_is_on()
    await message.reply_text(
        f"🔘 <b>Add Me button:</b> {'ON ✅' if on else 'OFF ❌'}\n\n"
        "<code>/addbtn on</code> — har broadcast me button\n"
        "<code>/addbtn off</code> — kisi me nahi (default)\n"
        "<code>/broadcast ... -btn</code> — sirf is broadcast me button\n"
        "<code>/broadcast ... -nobtn</code> — sirf is broadcast me button nahi"
    )


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-assistant" in query:
            query = query.replace("-assistant", "")
        if "-user" in query:
            query = query.replace("-user", "")
        query = re.sub(r"(?<!\S)-(?:nobtn|btn)\b", "", query).strip()
        if query == "":
            return await message.reply_text(_["broad_8"])

    use_btn = await want_button(message.text)
    markup = add_button() if use_btn else None

    IS_BROADCASTING = True
    await message.reply_text(
        _["broad_1"] + f"\n\n🔘 Add Me button: {'ON ✅' if use_btn else 'OFF ❌'}"
    )

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await app.copy_message(i, y, x, reply_markup=markup)
                    if message.reply_to_message
                    else await app.send_message(i, text=query, reply_markup=markup)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.copy_message(i, y, x, reply_markup=markup)
                    if message.reply_to_message
                    else await app.send_message(i, text=query, reply_markup=markup)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from SHUKLAMUSIC.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    await client.forward_messages(
                        dialog.chat.id, y, x
                    ) if message.reply_to_message else await client.send_message(
                        dialog.chat.id, text=query
                    )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())
        
