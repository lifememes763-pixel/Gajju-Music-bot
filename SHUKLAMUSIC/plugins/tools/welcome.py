# ----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shukla (https://github.com/itzshukla)
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
from logging import getLogger
from pyrogram import filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.mongo import mongodb
import config

LOGGER = getLogger(__name__)

# ── MongoDB Setup for persistent settings ──
weldb = mongodb.welcome_status

async def is_welcome_on(chat_id: int) -> bool:
    chat = await weldb.find_one({"chat_id": chat_id})
    if not chat:
        return True  # Default welcome ON
    return chat.get("welcome", "on") == "on"

async def welcome_on(chat_id: int):
    await weldb.update_one({"chat_id": chat_id}, {"$set": {"welcome": "on"}}, upsert=True)

async def welcome_off(chat_id: int):
    await weldb.update_one({"chat_id": chat_id}, {"$set": {"welcome": "off"}}, upsert=True)


# 📌 Welcome Image URL
WELCOME_IMG = "https://i.ibb.co/FLw0WWT6/x.jpg"

class temp:
    MELCOW = {}


@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        state = message.text.split(None, 1)[1].strip().lower()
        
        if state == "off":
            if not await is_welcome_on(chat_id):
                await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !**")
            else:
                await welcome_off(chat_id)
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɪɴ** {message.chat.title}")
        elif state == "on":
            if await is_welcome_on(chat_id):
                await message.reply_text("**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.**")
            else:
                await welcome_on(chat_id)
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɪɴ** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ!**")


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    
    # Check Mongo Database status
    if not await is_welcome_on(chat_id):
        return

    if member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != "kicked":
        user = member.new_chat_member.user

        if temp.MELCOW.get(f"welcome-{chat_id}") is not None:
            try:
                await temp.MELCOW[f"welcome-{chat_id}"].delete()
            except Exception as e:
                LOGGER.error(e)

        try:
            deep_link = f"tg://openmessage?user_id={user.id}"
            add_link = f"https://t.me/{app.username}?startgroup=true"
            
            # Bot Profile Mention for Hinata Click
            bot_mention = f"<a href='tg://user?id={app.id}'>𝐀ʟɪsᴀ</a>"
            username_str = f"@{user.username}" if user.username else "None"

            # Exact Original Layout Blockquote Message
            caption_text = (
                f"<blockquote>"
                f"~ 𝐖𝛜ʟᴄοᴍ𝛜 𝐓ο 𝐎υꝛ ֹ𝐆ʀᴏᴜᴘ 🌍°ʚɞ°🌷\n\n"
                f"<b>{member.chat.title}</b>\n"
                f"╔════════════════════\n"
                f"╠ 𝐍ᴀᴍᴇ ❥➸ {user.mention}\n"
                f"╠ 𝐔sᴇʀɴᴀᴍᴇ ❥➸ {username_str}\n"
                f"╠ 𝐔sᴇʀɪᴅ ❥➸ <code>{user.id}</code>\n"
                f"╚════════════════════ྀི ໒꒱ 💫\n\n"
                f"😊 ꧊᱂υɭ𝐞𝛅 🌷🦋\n\n"
                f"▫️𝐍ᴏ 𝐀ʙᴜsᴇ\n"
                f"▫️𝐍ᴏ 𝐏ʀᴏᴍᴏᴛᴇ\n"
                f"▫️𝐄𝐧ᴊᴏʏ 𝐓ʜᴇ 𝐌ᴜ𝐬ɪᴄ 𝐀ɴᴅ 𝐕ɪʙᴇ\n"
                f"▫️𝐃ᴍ 𝐍ᴏᴛ 𝐀ʟʟᴏᴡᴇᴅ 💎\n\n"
                f"╭───────────────❥\n"
                f"│ 𝐏σᴡ𝛜ʀ𝛜𝛅 𝐁𝛄 {bot_mention} 🩷\n"
                f"╰───────────────❥\n"
                f"</blockquote>"
            )

            # Styled Buttons (Primary, Success, Danger)
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="˹ ᴠɪᴇᴡ ᴍᴇᴍʙᴇꝛ ˼",
                        url=deep_link,
                        style=ButtonStyle.PRIMARY,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="˹ ᴋɪᴅɴᴀᴘ ᴍᴇ ˼",
                        url=add_link,
                        style=ButtonStyle.SUCCESS,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="˹ ϻʏ ϻᴧsᴛєʀ ˼",
                        url="https://t.me/Alexfaizan302",
                        style=ButtonStyle.DANGER,
                    )
                ]
            ])

            msg = await app.send_photo(
                chat_id,
                photo=WELCOME_IMG,
                caption=caption_text,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=buttons
            )

            temp.MELCOW[f"welcome-{chat_id}"] = msg

            # Auto-delete welcome message in 5 minutes (300 seconds)
            await asyncio.sleep(300)
            try:
                await msg.delete()
            except Exception:
                pass

        except Exception as e:
            LOGGER.error(e)
            
