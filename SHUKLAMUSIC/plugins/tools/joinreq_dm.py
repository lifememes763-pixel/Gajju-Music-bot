# ----------------------------------------------
# Join Request DM Plugin
# Path: SHUKLAMUSIC/plugins/tools/joinreq_dm.py
#
# Jab koi us group/channel me join request bhejta hai jahan bot admin hai
# (with "Invite Users" permission), bot us user ko DM me photo + message bhejta hai.
# -----------------------------------------------
import asyncio
import html

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup

import config
from SHUKLAMUSIC import app

# ================== SETTINGS ==================
PHOTO = "https://i.ibb.co/hFdRLqtZ/IMG-20261005-144514-837.jpg"

# {name} = user ka naam, {chat} = group/channel ka naam, {bot} = bot ka naam
CAPTION = (
    "🦋 <b>ʜᴇʏ, {name}!</b>\n\n"
    "🎵 <b>ᴛʜᴀɴᴋs ꜰᴏʀ ʀᴇǫᴜᴇsᴛɪɴɢ ᴛᴏ ᴊᴏɪɴ {chat}!</b>\n\n"
    "🪐 <b>ɪ'ᴍ {bot}</b>,\n"
    "ᴀ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ sᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ ꜰᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟs.\n\n"
    "🎧 <b>sᴇɴᴅ /start ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴛʜᴇ ʙᴏᴛ ᴍᴇɴᴜ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.</b>"
)

# True karoge to bot request ko auto-approve bhi kar dega
AUTO_APPROVE = False
# ==============================================


@app.on_chat_join_request()
async def join_request_dm(client, req: ChatJoinRequest):
    user = req.from_user
    chat = req.chat
    if not user or user.is_bot:
        return

    me = await client.get_me()
    caption = CAPTION.format(
        name=html.escape(user.first_name or "Friend"),
        chat=html.escape(chat.title or "the chat"),
        bot=html.escape(me.first_name or "Music Bot"),
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎧 ᴛᴀᴘ ᴛᴏ sᴇᴇ ᴍᴀɢɪᴄ", url=f"https://t.me/{me.username}?start=help")],
            [InlineKeyboardButton("🎵 ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{me.username}?startgroup=true")],
            [InlineKeyboardButton("🦋 ᴏᴡɴᴇʀ", url=f"https://t.me/{config.OWNER_USERNAME}")],
        ]
    )

    try:
        await client.send_photo(
            user.id,
            photo=PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    except Exception:
        # user ne DM band rakhe ya bot block kiya -> chup-chap skip
        pass

    if AUTO_APPROVE:
        try:
            await asyncio.sleep(1)
            await client.approve_chat_join_request(chat.id, user.id)
        except Exception:
            pass
          
