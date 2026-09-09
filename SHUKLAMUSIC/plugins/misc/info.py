# -*- coding: utf-8 -*-
# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# -----------------------------------------------
import asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode, ButtonStyle
from SHUKLAMUSIC import app

INFO_TEXT = (
    "<blockquote><u><b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>\n\n"
    "<b>● ᴜsᴇʀ ɪᴅ ➠</b> <code>{}</code>\n"
    "<b>● ᴜsᴇʀɴᴀᴍᴇ ➠</b> <code>@{}</code>\n"
    "<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {}\n"
    "<b>● ᴜsᴇʀ sᴛᴀᴛᴜs ➠</b> {}\n"
    "<b>● ᴜsᴇʀ ᴅᴄ ɪᴅ ➠</b> {}</blockquote>"
)

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "Recently Active"
        elif x == enums.UserStatus.LAST_WEEK:
            return "Active Last Week"
        elif x == enums.UserStatus.LONG_AGO:
            return "Seen Long Ago"
        elif x == enops.UserStatus.OFFLINE if hasattr(enums, 'UserStatus') else False: # safe fallback
            return "Offline"
        elif x == enums.UserStatus.ONLINE:
            return "Online"
        else:
            return "Unknown"
    except:
        return "Not Available"

@app.on_message(filters.command(["info", "information", "userinfo", "whois"], prefixes=["/", "!"]))
async def userinfo(_, message: Message):
    chat_id = message.chat.id
    target_user = message.from_user.id if message.from_user else None

    try:
        # Check if user passed an argument or replied to a message
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            args = message.text.split(None, 1)[1].strip()
            # Agar user ID di hai toh usko integer mein convert karo, nahi toh username rehne do
            if args.isdigit() or (args.startswith("-") and args[1:].isdigit()):
                target_user = int(args)
            else:
                target_user = args  # Username ya t.me link handling

        if not target_user:
            return await message.reply_text("<blockquote>❌ <b>Please provide a username, user ID, or reply to a user!</b></blockquote>", parse_mode=ParseMode.HTML)

        # Fetch user info safely (yeh ab IDs aur Usernames dono ke liye perfectly chalega)
        user_info = await app.get_chat(target_user)
        user = await app.get_users(target_user)
        status = await userstatus(user.id)

        uid = user_info.id
        dc_id = user.dc_id or "N/A"
        username = user_info.username or "N/A"
        mention = user.mention

        # Profile URL generation
        if user_info.username:
            profile_url = f"https://t.me/{user_info.username}"
        else:
            profile_url = f"tg://user?id={user.id}"

        await app.send_message(
            chat_id,
            text=INFO_TEXT.format(uid, username, mention, status, dc_id),
            reply_to_message_id=message.id,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👤 ᴜsᴇʀ ᴘʀᴏғɪʟᴇ", url=profile_url, style=ButtonStyle.PRIMARY)
                    ],
                    [
                        InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close", style=ButtonStyle.DANGER)
                    ]
                ]
            ),
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>❌ <b>Error:</b> <code>{str(e)}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
