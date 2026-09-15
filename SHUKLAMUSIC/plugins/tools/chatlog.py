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

import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
from pyrogram.errors import RPCError
from config import LOGGER_ID as LOG_GROUP_ID
from SHUKLAMUSIC import app

photo = [
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
]


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):
    chat = message.chat

    for member in message.new_chat_members:
        if member.id != app.id:
            continue

        try:
            count = await app.get_chat_members_count(chat.id)
        except RPCError:
            count = "Unavailable"

        try:
            link = await app.export_chat_invite_link(chat.id)
        except RPCError:
            link = None

        chat_username = (
            f"@{chat.username}"
            if chat.username
            else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴘ"
        )

        chat_link = (
            f'<a href="{link}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
            if link
            else "𝐔ɴᴀᴠᴀɪʟᴀʙʟᴇ"
        )

        added_by = (
            message.from_user.mention
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )

        msg = (
            "╭━━━〔 🌸 𝐀ʟɪsᴀ ✦ 𝐌ᴜsɪᴄ 〕━━━╮\n"
            "┃\n"
            "┃ 🎵 <b>𝐁ᴏᴛ 𝐀ᴅᴅᴇᴅ 𝐈ɴ 𝐍ᴇᴡ 𝐆ʀᴏᴜᴘ</b>\n"
            "┃\n"
            f"┃ 📌 <b>𝐂ʜᴀᴛ:</b> {chat.title}\n"
            f"┃ 🆔 <b>𝐈ᴅ:</b> <code>{chat.id}</code>\n"
            f"┃ 🔐 <b>𝐔sᴇʀɴᴀᴍᴇ:</b> {chat_username}\n"
            f"┃ 🛰 <b>𝐋ɪɴᴋ:</b> {chat_link}\n"
            f"┃ 👥 <b>𝐌ᴇᴍʙᴇʀs:</b> {count}\n"
            f"┃ 👤 <b>𝐀ᴅᴅᴇᴅ 𝐁ʏ:</b> {added_by}\n"
            "┃\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )

        buttons = []
        if link:
            buttons = [[
                InlineKeyboardButton(
                    "👀 ᴠɪᴇᴡ ɢʀᴏᴜᴘ",
                    url=link,
                    style=ButtonStyle.DANGER
                )
            ]]

        await app.send_photo(
            LOG_GROUP_ID,
            photo=random.choice(photo),
            caption=msg,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        )


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    try:
        me = await app.get_me()

        if message.left_chat_member.id != me.id:
            return

        remove_by = (
            message.from_user.mention
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )

        title = message.chat.title or "𝐔ɴᴋɴᴏᴡɴ 𝐂ʜᴀᴛ"

        username = (
            f"@{message.chat.username}"
            if message.chat.username
            else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        )

        chat_id = message.chat.id

        left = (
            "╭━━━〔 🚫 𝐀ʟɪsᴀ ✦ 𝐌ᴜsɪᴄ 〕━━━╮\n"
            "┃\n"
            "┃ <b>#𝐋ᴇғᴛ_𝐆ʀᴏᴜᴘ</b>\n"
            "┃\n"
            f"┃ 📌 <b>𝐂ʜᴀᴛ:</b> {title}\n"
            f"┃ 🆔 <b>𝐈ᴅ:</b> <code>{chat_id}</code>\n"
            f"┃ 🔐 <b>𝐔sᴇʀɴᴀᴍᴇ:</b> {username}\n"
            f"┃ 👤 <b>𝐑ᴇᴍᴏᴠᴇᴅ 𝐁ʏ:</b> {remove_by}\n"
            f"┃ 🤖 <b>𝐁ᴏᴛ:</b> @{app.username}\n"
            "┃\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )

        await app.send_photo(
            LOG_GROUP_ID,
            photo=random.choice(photo),
            caption=left,
        )

    except RPCError:
        return
    except Exception:
        return
